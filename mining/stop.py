import os
import signal

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['Coin']+")")

    pinfo = config.get_status(coin)
    if pinfo is None:
        print coin['Coin']+": There is no process mining "+coin['Coin']
        return 1
    else:
        if config.arguments['--dryrun']:
            print "kill SIGKILL " + str(pinfo['pid'])
        else:
            os.kill(pinfo['pid'], signal.SIGKILL)
    return None

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['Coin']+")")

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['Coin']+")")
    return 0
