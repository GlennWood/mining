from __future__ import print_function
import subprocess
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
    global COUNT_STATUS
    if config.SCOPE:
        return process_scope(self,config, coin)

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
        print(pinfo['coin'] + ': [' + str(pinfo['pid']) + '] ' + cmdline)
        COUNT_STATUS += 1

    return config.ALL_MEANS_ONCE

# Handle 'status' operation within the given --scope
def process_scope(self, config, coin):
    sttyColumns = int(subprocess.check_output(['stty', 'size']).split()[1])
    for key in config.ANSIBLE_HOSTS:
        host = config.ANSIBLE_HOSTS[key]
        if config.SCOPE.upper() == 'ALL' or config.SCOPE.upper() in host['hostname'].upper():
            proc = subprocess.Popen(['ssh', '-l', config.SHEETS['Globals']['MINERS_USER']['VALUE'], '-o', 'StrictHostKeyChecking=no', 
                        host['ip'], 'miners', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            out, err = proc.communicate(None)
            if out:
                hostname = '['+host['hostname']+']            '
                for ln in out.split('\n'):
                    ln = ln.rstrip()
                    regex = re.compile(r'(.*?)[[][^]]*[]](.*)', re.DOTALL)
                    match = regex.match(ln)
                    if match and match.lastindex is 2: ln = match.group(1) + match.group(2)
                    if ln:
                        if not config.WIDE_OUT and len(ln) > sttyColumns: ln = ln[0:sttyColumns-16]+'...'
                        print("%.12s %s"%(hostname+'            ', ln))
                    hostname = '            '
            if err:
                hostname = '['+host['hostname']+']            '
                for ln in out.split('\n'):
                    print("%.12s %s"%(hostname+'            ', err.rstrip()))
                    hostname = '            '


def initialize(self, config, coin):
    global COUNT_STATUS
    COUNT_STATUS = 0
    return 0

def finalize(self, config, coin):
    global COUNT_STATUS
    if COUNT_STATUS is 0:
        config.RC_MAIN = 1
    return 0
