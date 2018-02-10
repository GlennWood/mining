#!/usr/bin/python

"""
Usage: monitor.py OPERATION [-htvX] [COIN] ...

Arguments:
  OPERATION  start | stop | shutdown | status | list | logs
               (a comma-separated list of OPERATIONs)
  COIN       Apply OPERATION to this coin's monitor

Options:
  -t  send text message when abnormal behavior detected
  -X  dryrun, print configured behavior, then exit
  -h  print help, then exit
  -v  verbose mode
"""

from __future__ import print_function
import os
import sys
import daemon
import signal
import lockfile
import logging
import subprocess
import schedule # Ref: https://github.com/dbader/schedule
import time

sys.path.insert(0,'/opt/mining/mining')
sys.path.insert(0,'/opt/mining/monitor')
import config
import importlib

global logger

### Ref: http://docopt.org/
### Ref: https://github.com/docopt/docopt
from docopt import docopt
config = config.Config(docopt(__doc__, argv=None, help=True, version=None, options_first=False))
arguments = config.arguments
OPERATION = arguments.get('OPERATION')

config.PIDFILE = '/var/local/ramdisk/monitor.pid'

## Run the 'process' function of the given module
def run_module_process(mod_name):
    module_name = 'mon_'+mod_name.replace('-','_')
    module =  importlib.import_module(module_name)
    method = getattr(module, 'process')
    RC = method(module, config, arguments)
    if RC != 0: config.logger.warn(module_name+'.process() returned RC=%i',RC)
    return RC

## Run mon_miners.process()
def monitor_miners(): return run_module_process('miners')
def cap_diff(): return run_module_process('cap-diff')



def shutdown(signum, frame):  # signum and frame are mandatory
    global logger
    if frame: frame = frame
    logger.info("Received shutdown signal "+str(signum))
    logger.info("Miners Monitor stopped, pid=%i", str(os.getpid()))
    if signum == signal.SIGTERM: sys.exit(0)
    if signum == signal.SIGTSTP: sys.exit(0)
    sys.exit(1)





config.logger = logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logFH = logging.FileHandler("/var/log/mining/monitor.log")
logFH.setFormatter(logging.Formatter('%(asctime)s %(levelname)s - %(message)s'))
logger.addHandler(logFH)


if OPERATION not in ['start','miners']:
    try:
        module_name = arguments.get('OPERATION').replace('-','_')
        RC = run_module_process(module_name)
    except AttributeError as ex:
        if arguments.get('-v'): print(ex)
        print ("Module '"+module_name+"' has no process() method.", file=sys.stderr)
        sys.exit(1)
    sys.exit(RC)


##################################################################################
## Check against any other miners monitor already running
if os.path.exists(config.PIDFILE+'.lock') and arguments.get('OPERATION') != 'cap-diff':
    print("Found a lockfile at "+config.PIDFILE+".lock! It seems that monitor-miners daemon is already running, ", end='')
    #os.system('ps -Af|grep -v grep|grep -v '+str(os.getpid())+'|grep monitor-miners')
    proc = subprocess.Popen('ps -Af|grep -v grep|grep -v '+str(os.getpid())+'|grep monitor-miners',stdout=subprocess.PIPE,shell=True)
    (out, err) = proc.communicate()
    print (out)
    if err: print (err)
    sys.exit(1)
elif os.path.exists(config.PIDFILE): os.remove(config.PIDFILE)

# Fork this!
newpid = os.fork()
if newpid == 0:
    print("Mining monitor started.")
    sys.exit(0)

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
                        pidfile=lockfile.LockFile(config.PIDFILE)
                    ):
    pid = os.getpid()
    with open(config.PIDFILE,'w') as fh: fh.write(str(pid))

    schedule.every(5).minutes.do(monitor_miners)
    schedule.every().day.at("4:30").do(cap_diff)
    logger.info("Miners Monitor started, pid=%i", pid)

    while True:
        schedule.run_pending()
        time.sleep(1)

    logger.error("unexpected exit")
    print >> sys.stderr, "unexpected exit"

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
