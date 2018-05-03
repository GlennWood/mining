import re
import psutil
import types

### TODO: ls -1stoh /var/log/mining/ETH-miner.*

def get_status(coin, exclude_pids=[], exclude_cmdlines=[]):

    result = []
    names = []

    if coin is None:
        names = None
    elif isinstance(coin, types.ListType):
        names = coin
    else:
        names.append(coin['COIN'].upper())

    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
            cmdline = ' '.join(pinfo['cmdline'])
            if pinfo['pid'] in exclude_pids: continue
            if 'tail -f' in cmdline: continue
            for cmd in exclude_cmdlines:
                if cmdline.find(cmd) >= 0: continue
            for name in names:
                if cmdline.find(name+'-miner') >= 0 or cmdline.find('c='+name) >= 0:
                    pinfo['coin'] = name
                    result.append(pinfo)
        except psutil.NoSuchProcess:
            pass

    if coin is None or isinstance(coin, types.ListType):
        return result
    elif len(result) > 0:
        return result[0]
    else:
        return None


def process(self, config, coin):
    coins = []
    if config.ALL_COINS:
        coins = config.arguments['COIN']
    else:
        coins.append(coin['COIN'])
    pinfos = get_status(coins)

    if pinfos is None:
        if not config.ALL_COINS or config.VERBOSE:
            print(coin['COIN']+": There is no process mining "+coin['COIN'])
        return 0

    for pinfo in pinfos:
        cmdline = ' '.join(pinfo['cmdline'])
        regex = re.compile(r'(.*?)(-[ez]psw[= ]|--pass |-p )\s*(\S*)(.*)\s*', re.DOTALL)
        match = regex.match(cmdline)
        if not match is None and match.lastindex is 4 and not 'c=' in match.group(3):
            cmdline = match.group(1)+match.group(2)+'{x} '+match.group(4)
        
        # URL regex= s/.*(-\wpool|--server|-F|--url=)\s*([A-Za-z0-9./:_+-]{1,99}).*/\2/'
        print pinfo['coin'] + ': [' + str(pinfo['pid']) + '] ' + cmdline
    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    #if config.VERBOSE: print(__name__+".initialize("+coin['COIN']+")")
    return 0

def finalize(self, config, coin):
    #if config.VERBOSE: print(__name__+".finalize("+coin['COIN']+")")
    return 0
