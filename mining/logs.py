import os

def process(self, config, coin):
    global TAIL_LOG_FILES
    if config.VERBOSE: print(__name__+".process("+coin['Coin']+")")

    TAIL_LOG_FILES.extend(['/var/log/mining/'+config.WORKER_NAME+'.log', ' /var/log/mining/'+config.WORKER_NAME+'.err'])

    return 0

def initialize(self, config, coin):
    global TAIL_LOG_FILES
    TAIL_LOG_FILES = []
    if config.VERBOSE: print(__name__+".initialize("+coin['Coin']+")")
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    global TAIL_LOG_FILES
    if config.VERBOSE: print(__name__+".finalize("+coin['Coin']+")")
    if config.DRYRUN:
        print 'tail -f ' + ' '.join(TAIL_LOG_FILES)
    else:
        os.system('tail -f ' + ' '.join(TAIL_LOG_FILES))
    return config.ALL_MEANS_ONCE
