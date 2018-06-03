from __future__ import print_function
import stop
import start
import status
import time
import sys

def process(self, config, coin):

    if config.DRYRUN:
        stop.process(self, config, coin[0])
        pinfo = status.get_status(coin[0])
        print('timeout 60 wait '+str(pinfo['pid']))
        print('[ $? = 0 ] && ',end='')
        start.process(self, config, coin[1])
    else:
        print("Stopping "+coin[0]['COIN'])
        stop.process(self, config, coin[0])
    
        pinfo = status.get_status(coin[0])
        t = 0
        while pinfo is not None and t < 60:
            t += 1
            print('Waiting ... '+str(t)+' '),;sys.stdout.flush()
            time.sleep(0.5)
            print ('\r'),;sys.stdout.flush()
            pinfo = status.get_status(coin[0])
        if t >= 60:
            print("FAIL: Process mining "+coin[0]['COIN']+" did not stop!")
            return 1
    
        print("Starting "+coin[1]['COIN'])
        start.process(self, config, coin[1])

    return 0

def initialize(self, config, coin):

    pinfo = status.get_status(coin[0])
    if pinfo is None:
        print(coin[0]['COIN']+": There is no process mining "+coin[0]['COIN'])
        return 1

    pinfo = status.get_status(coin[1])
    if pinfo is not None and coin[0]['COIN'] is not coin[1]['COIN']:
        print(coin[1]['COIN']+": There is already a process mining "+coin[1]['COIN'])
        return 1

    stop.initialize(self, config, coin)
    start.initialize(self, config, coin)

    return 0

def finalize(self, config, coin):
    start.finalize(self, config, coin)
    stop.finalize(self, config, coin)
    return 0
