## Check monitor's status and exit
from __future__ import print_function
import os
import subprocess

def process(self, config, arguments):
    if arguments.get('OPERATION') == 'status':
        if os.path.exists(config.PIDFILE+'.lock'):
            print("Found a lockfile at "+config.PIDFILE+".lock", end='')
            with open(config.PIDFILE,'r') as fh: pid = fh.readline()
            print(', pid='+pid)
            proc = subprocess.Popen('ps -Af|grep -v grep|grep -v '+str(os.getpid())+'|grep -v "tail -f"|grep monitor',stdout=subprocess.PIPE,shell=True)
            (out, err) = proc.communicate()
            print(out,end='')
            if err: print(err,end='')
            return 0
        else:
            print("Miners monitor is not running.")
            return 1
