import os
import subprocess

def process(self, config, coin):
    global TAIL_LOG_FILES
    if config.VERBOSE: print(__name__+".process("+coin['Coin']+")")

    for ext in ['.log','.err','.out']:
        logName = '/var/log/mining/'+config.WORKER_NAME+ext
        if os.path.isfile(logName):
            TAIL_LOG_FILES.append(logName)
    return 0

def initialize(self, config, coin):
    global TAIL_LOG_FILES
    TAIL_LOG_FILES = ['tail', '-f']
    if config.VERBOSE: print(__name__+".initialize("+coin['Coin']+")")
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    global TAIL_LOG_FILES
    if config.VERBOSE: print(__name__+".finalize("+coin['Coin']+")")
    cmd = '/usr/bin/tail -f ' + ' '.join(TAIL_LOG_FILES)
    if config.DRYRUN:
        print cmd
    else:

        try:
            subprocess.call(TAIL_LOG_FILES)
        except KeyboardInterrupt:
            if config.VERBOSE: print 'exit: miners logs '+' '.join(config.arguments['COIN'])

    return config.ALL_MEANS_ONCE
