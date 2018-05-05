import os
import signal
import status
import start

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['COIN']+")")

    # We have this way of handing all this off to SystemD ...
    miner = coin['MINER']
    client = None
    if miner in config.SHEETS['Clients']:
        client = config.SHEETS['Clients'][miner]
        miner = client['EXECUTABLE']
    if miner in start.MINER_TO_BINARY: miner = start.MINER_TO_BINARY[miner]
    if miner.endswith('.service'):
        miner = miner.replace('.service','')
        cmd = 'sudo service '+miner+' stop'
        if config.DRYRUN:
            print cmd
        else:
            os.system(cmd)
        return 0
    
    coins = []
    if config.ALL_COINS:
        coins = config.arguments['COIN']
    else:
        coins.append(coin['COIN'])
    pinfos = status.get_status(coins)

    if pinfos is None:
        print coin['COIN']+": There is no process mining "+coin['COIN']
        return 1
    else:
        pids = ''
        if config.arguments['--dryrun']:
            for pinfo in pinfos:
                pids += ' ' + str(pinfo['pid'])
            print "sudo kill -s KILL" + pids
        else:
            for pinfo in pinfos:
                try:
                    os.kill(pinfo['pid'], signal.SIGKILL)
                except OSError:
                    print "You must be root to stop this "+coin['COIN']+" miner; e.g. 'sudo kill -s KILL " + str(pinfo['pid'])+"'"
    return 0

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['COIN']+")")
    return 0

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['COIN']+")")
    return 0
