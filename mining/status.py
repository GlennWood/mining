import re
import psutil

def get_status(coin):

    name = coin['Coin'].upper()
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
            cmdline = ' '.join(pinfo['cmdline'])
            if 'tail -f' in cmdline: continue
            if cmdline.find(name+'-miner') >= 0 or cmdline.find('c='+name) >= 0:
                return pinfo
        except psutil.NoSuchProcess:
            pass
    return None
      
  

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['Coin']+")")

    pinfo = get_status(coin)
    if pinfo is None:
        if not config.ALL_COINS or config.VERBOSE:
            print(coin['Coin']+": There is no process mining "+coin['Coin'])
        return 1

    cmdline = ' '.join(pinfo['cmdline'])
    regex = re.compile(r'(.*?)(-[ez]psw[= ]|-p )\s*(\S*)(.*)\s*', re.DOTALL)
    match = regex.match(cmdline)
    if not match is None and match.lastindex is 4 and not 'c=' in match.group(3):
        cmdline = match.group(1)+match.group(2)+'{x} '+match.group(4)
    
    # URL regex= s/.*(-\wpool|--server|-F|--url=)\s*([A-Za-z0-9./:_+-]{1,99}).*/\2/'
    print coin['Coin'] + ': ' + cmdline
    return 0

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['Coin']+")")

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['Coin']+")")
    return 0
