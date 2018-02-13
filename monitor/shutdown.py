import os
import signal
import status

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process()")
    if coin: coin = coin

    pInfo = status.get_status(None,[os.getpid()],['-miner '])
    if pInfo is None:
        print "There is no process running monitor-miners."
        return 1
    else:
        if config.VERBOSE: print(pInfo)
        if config.arguments['--dryrun']:
            print "sudo kill SIGKILL " + str(pInfo['pid'])
        else:
            try:
                os.kill(pInfo['pid'], signal.SIGKILL)
            except OSError as ex:
                print ex
                print "You must be root to stop monitor-miners; e.g. 'sudo kill SIGKILL " + str(pInfo['pid'])+"'"
    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize()")
    if coin: coin = coin
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize()")
    if coin: coin = coin
    return config.ALL_MEANS_ONCE

