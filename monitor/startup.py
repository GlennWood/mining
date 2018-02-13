import os
import status

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process()")
    if coin: coin = coin

    pInfo = status.get_status(None,[os.getpid()],['-miner '])
    if pInfo is not None:
        if config.VERBOSE: print(pInfo)
        print "monitor-miners is already running."
        return 1
    else:
        if config.arguments['--dryrun']:
            print "sudo monitor-miners start"
        else:
            try:
                os.system('monitor-miners start')
            except OSError as ex:
                if config.VERBOSE: print ex
                print "You must be root to start monitor-miners; e.g. 'sudo monitor-miners start'"
    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize()")
    if coin: coin = coin
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize()")
    if coin: coin = coin
    return config.ALL_MEANS_ONCE

