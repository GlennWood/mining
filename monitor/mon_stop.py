## Check monitor's status and exit
import os
import sys
import signal

## if OPERATION=status, check monitor's status and exit
def process(self, config, arguments):
    if os.path.exists(config.PIDFILE+'.lock'):
        with open(config.PIDFILE,'r') as fh: pid = fh.readline()
        if arguments.get('-X'):
            print("kill "+str(pid))
        else:
            os.kill(int(pid), signal.SIGTERM)
        sys.exit(0)
    else:
        print ("Miners monitor appears to be stopped already.")
        sys.exit(1)

