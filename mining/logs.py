
import os

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['Coin']+")")

    if config.TAIL_LOG_FILES:
        config.TAIL_LOG_FILES += ' ' + '/var/log/mining/'+config.WORKER_NAME+'.log' + ' /var/log/mining/'+config.WORKER_NAME+'.err'
    else:
        config.TAIL_LOG_FILES = '/var/log/mining/'+config.WORKER_NAME+'.log' + ' /var/log/mining/'+config.WORKER_NAME+'.err'

    return 0

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['Coin']+")")

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['Coin']+")")
    if config.TAIL_LOG_FILES != '': os.system(config.DRYRUN+'tail -f ' + config.TAIL_LOG_FILES)
    return 0
