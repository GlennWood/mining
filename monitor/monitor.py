#!/usr/bin/python

"""
Usage: monitor.py OPERATION [-hv] [COIN] ...

Arguments:
  OPERATION  start | stop | shutdown | status | list | logs
               (a comma-separated list of OPERATIONs)
  COIN       Apply OPERATION to this coin's monitor

Options:
  -h  print help, then exit
  -v  verbose mode
"""

import os
import sys
import textmsg
import daemon
import signal
import lockfile
import logging
import time
import subprocess

sys.path.insert(0,'/opt/mining/mining')
sys.path.insert(0,'/opt/mining/monitor')
import config
import status
import fibo_meter

### Ref: http://docopt.org/
### Ref: https://github.com/docopt/docopt
from docopt import docopt
config = config.Config(docopt(__doc__, argv=None, help=True, version=None, options_first=False))
arguments = config.arguments
global logger

def shutdown(signum, frame):  # signum and frame are mandatory
    global logger
    logger.info("Received shutdown signal "+str(signum))
    logger.info("Miners Monitor stopped")
    if signum == signal.SIGTERM: sys.exit(0)
    if signum == signal.SIGTSTP: sys.exit(0)
    sys.exit(1)

PIDFILE = '/var/local/ramdisk/monitor.pid'
if os.path.exists(PIDFILE+'.lock'):
    print("Found a lockfile at "+PIDFILE+".lock! It seems that monitor-miners daemon is already running.")
    #os.system('ps -Af|grep -v grep|grep -v '+str(os.getpid())+'|grep monitor-miners')
    proc = subprocess.Popen('ps -Af|grep -v grep|grep -v '+str(os.getpid())+'|grep monitor-miners',stdout=subprocess.PIPE,shell=True)
    (out, err) = proc.communicate()
    print out
    sys.exit(1)
elif os.path.exists(PIDFILE): os.remove(PIDFILE)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logFH = logging.FileHandler("/var/log/mining/monitor.log")
logFH.setFormatter(logging.Formatter('%(asctime)s %(levelname)s - %(message)s'))
logger.addHandler(logFH)

try:
    # Fork this!
    newpid = os.fork()
    if newpid == 0: sys.exit(0)

    try: os.setsid() # if 'fork failed: 1 (Operation not permitted)', it's just due to python's 
    except OSError as ex: newpid = newpid  #  exception when you are already the group-leader ... 
    os.umask(0)
    
    ### Ref: https://dpbl.wordpress.com/2017/02/12/a-tutorial-on-python-daemon/
    with daemon.DaemonContext(chroot_directory=None,
                            working_directory='/var/mining',
                            files_preserve = [logFH.stream],
                            signal_map={
                                signal.SIGTERM: shutdown,
                                signal.SIGTSTP: shutdown
                            },
                            pidfile=lockfile.LockFile(PIDFILE)
                        ):
        pid = os.getpid()
        with open(PIDFILE,'w') as fh: fh.write(str(pid))
        fiboMeter = fibo_meter.FiboMeter()
        logger.info("Miners Monitor started, pid=%i", pid)
        
        monitorPeriod = 300
        loopCount = 1
        while True:
            time.sleep(monitorPeriod)
            pInfos = status.get_status(None)
            if pInfos != None and len(pInfos) > 0:
                logger.info("All systems GO!")
            else:
                logger.error("There are no mining processes running at this time!")
                if fiboMeter.fibo_next(loopCount):
                    textmsg.send(os.getenv('HOSTNAME')+": Not mining!")
            loopCount += 1;

except AttributeError, ex:
    print >> sys.stderr, "fork of 'monitor' failed: %s" % str(ex)
    logger.error("fork of 'monitor' failed: %s" % str(ex))
    sys.exit(2)
except OSError, ex:
    print >> sys.stderr, "fork of 'monitor' failed: %s" % str(ex)
    logger.error("fork of 'monitor' failed: %s" % str(ex))
    sys.exit(1)
except SystemExit:
    logger.info("SystemExit")
    sys.exit
except:
    ex = sys.exc_info()[0]
    print ( ex )
    sys.exit(3)

'''
    SIGHUP        1       Term    Hangup detected on controlling terminal
                                     or death of controlling process
    SIGINT        2       Term    Interrupt from keyboard
    SIGQUIT       3       Core    Quit from keyboard
    SIGILL        4       Core    Illegal Instruction
    SIGABRT       6       Core    Abort signal from abort(3)
    SIGFPE        8       Core    Floating-point exception
    SIGKILL       9       Term    Kill signal
    SIGSEGV      11       Core    Invalid memory reference
    SIGPIPE      13       Term    Broken pipe: write to pipe with no
                                     readers; see pipe(7)
    SIGALRM      14       Term    Timer signal from alarm(2)
    SIGTERM      15       Term    Termination signal
    SIGUSR1   30,10,16    Term    User-defined signal 1
    SIGUSR2   31,12,17    Term    User-defined signal 2
    SIGCHLD   20,17,18    Ign     Child stopped or terminated
    SIGCONT   19,18,25    Cont    Continue if stopped
    SIGSTOP   17,19,23    Stop    Stop process
    SIGTSTP   18,20,24    Stop    Stop typed at terminal
    SIGTTIN   21,21,26    Stop    Terminal input for background process
    SIGTTOU   22,22,27    Stop    Terminal output for background process

    SIGIOT         6        Core    IOT trap. A synonym for SIGABRT
    SIGEMT       7,-,7      Term    Emulator trap
    SIGSTKFLT    -,16,-     Term    Stack fault on coprocessor (unused)
    SIGIO       23,29,22    Term    I/O now possible (4.2BSD)
    SIGCLD       -,-,18     Ign     A synonym for SIGCHLD
    SIGPWR      29,30,19    Term    Power failure (System V)
    SIGINFO      29,-,-             A synonym for SIGPWR
    SIGLOST      -,-,-      Term    File lock lost (unused)
    
'''
