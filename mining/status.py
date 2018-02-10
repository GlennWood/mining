import re
import psutil

def get_status(coin,exclude_pids=[]):

    result = []

    if coin is None:
        name = ''
    else:
        name = coin['COIN'].upper()

    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
            cmdline = ' '.join(pinfo['cmdline'])
            if pinfo['pid'] in exclude_pids: continue
            if 'tail -f' in cmdline: continue
            if cmdline.find(name+'-miner') >= 0 or cmdline.find('c='+name) >= 0:
                result.append(pinfo)
        except psutil.NoSuchProcess:
            pass

    if coin is None:
        return result
    elif len(result) > 0:
        return result[0]
    else:
        return None


def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['COIN']+")")

    pinfo = get_status(coin)
    if pinfo is None:
        if not config.ALL_COINS or config.VERBOSE:
            print(coin['COIN']+": There is no process mining "+coin['COIN'])
        return 1

    cmdline = ' '.join(pinfo['cmdline'])
    regex = re.compile(r'(.*?)(-[ez]psw[= ]|--pass |-p )\s*(\S*)(.*)\s*', re.DOTALL)
    match = regex.match(cmdline)
    if not match is None and match.lastindex is 4 and not 'c=' in match.group(3):
        cmdline = match.group(1)+match.group(2)+'{x} '+match.group(4)
    
    # URL regex= s/.*(-\wpool|--server|-F|--url=)\s*([A-Za-z0-9./:_+-]{1,99}).*/\2/'
    print coin['COIN'] + ': ' + cmdline
    return 0

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['COIN']+")")

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['COIN']+")")
    return 0
