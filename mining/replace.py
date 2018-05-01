import stop
import start
import status

def process(self, config, coin):
    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    #coins = coin.split(':')
    pinfo = status.get_status(coin[0])
    if pinfo is None:
        if not config.ALL_COINS or config.VERBOSE:
            print(coin[0]['COIN']+": There is no process mining "+coin[0]['COIN'])
        return 1
    print "Stopping "+coin[0]['COIN']
    return 0

def finalize(self, config, coin):
    #coins = coin.split(':')
    pinfo = status.get_status(coin[1])
    if pinfo is not None:
        print(coin[1]['COIN']+": There is already a process mining "+coin[1]['COIN'])
        return 1
    print "Starting "+coin[1]['COIN']
    return 0
