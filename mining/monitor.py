import os
import sys
import textmsg
import daemon
import signal
import lockfile
import logging
import time

### TODO: Ideas for start/stop/status - https://pagure.io/python-daemon/blob/master/f/daemon/runner.py#_82

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['Coin']+")")

    if config.DRYRUN:
        print 'daemon monitor'
        return 0

    try:
        # Fork this!
        newpid = os.fork()
        if newpid == 0: return 0

        try:
            os.setsid()
        except OSError as ex:# 'fork of './ccminer' failed: 1 (Operation not permitted)' 
            newpid = newpid#  due to python's exception when you are already the group-leader ... 
        os.umask(0)
        
        ### Ref: https://stackoverflow.com/a/15329299   
        mLogger = logging.getLogger()
        mLogger.setLevel(logging.INFO)
        mLog = mLogger.FileHandler("/var/log/mining/monitor.log")
        mLogger.addHandler(mLog)
        eLogger = logging.getLogger()
        eLogger.setLevel(logging.DEBUG)
        eLog = eLogger.FileHandler("/var/log/mining/monitor.err")
        eLogger.addHandler(eLog)

        ### Ref: https://dpbl.wordpress.com/2017/02/12/a-tutorial-on-python-daemon/
        with daemon.DaemonContext(chroot_directory=None,
                                working_directory='/var/mining',
                                files_preserve = [eLog.stream, mLog.stream],
                                signal_map={
                                    signal.SIGTERM: shutdown,
                                    signal.SIGTSTP: shutdown },
                                pidfile=lockfile.FileLock('/var/run/miners/monitor.pid')
                            ):
            while True:
                time.sleep(60)
                mLogger.info("Monitor is running")

    except OSError, ex:
        print >> sys.stderr, "fork of 'monitor' failed: %d (%s)" % (ex.errno, ex.strerror)
        sys.exit(1)
    except:
        ex = sys.exc_info()[0]
        print ( ex )


    def shutdown(signum, frame):  # signum and frame are mandatory
        eLogger.info("Received signal "+str(signum)+"; exiting")
        if signum == signal.SIGTERM: sys.exit(0)
        if signum == signal.SIGTSTP: sys.exit(0)
        sys.exit(1)

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['Coin']+")")
    return 0

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['Coin']+")")
    return 0
