#!/usr/bin/python3
from __future__ import print_function
import sys
from os import walk
import balances
### Ref: http://python-future.org/compatible_idioms.html
from builtins import range

EXTRA_HELP = {
    'balances': 'BALANCES',
    '--scope': 'BALANCES',
    'start': 'COINS',
    'stop': 'COINS',
    'logs': 'LOGS',
    'whattomine': '--scope -v',
    'restart': '-v -X',
    'devices': '-v'
}

if len(sys.argv) > 2: # this means user is beyond the 'miners <tab><tab>' stage
    #sys.argv.pop(0)
    for idx in range(len(sys.argv)-1,0,-1):
        prev = sys.argv[idx]
        if prev in EXTRA_HELP:
            if EXTRA_HELP[prev] == 'COINS':
                import config
                config = config.Config(None)
                coin = [ item.lower() for item in config.arguments['COIN'] ]
                print(' '.join(coin))
                sys.exit()
            elif EXTRA_HELP[prev] == 'LOGS':
                logs = []
                for (dirpath, dirnames, filenames) in walk('/var/log/mining'):
                    logs.extend(filenames)
                    break
                logs = [log.split('-')[0] for log in logs]
                print(' '.join(logs))
                sys.exit()  
            elif EXTRA_HELP[prev] == 'BALANCES':
                balances.bash_completion(prev)
                sys.exit()
            else:
                print(EXTRA_HELP[prev])
                sys.exit()


operations = []
for (dirpath, dirnames, filenames) in walk('/opt/mining/mining'):
    operations.extend(filenames)
    operations.extend(dirnames)
    break
operations = [op for op in operations if not op.endswith('.pyc') and op != '__pycache__'] # filter out *.pyc compile artifacts
operations = [op.replace('.py','') for op in operations] # strip '.py' from the filenames
# some "modules" are in /opt/mining/mining that are not operations, and TODO belong somewhere else.
operations = [op for op in operations if '__init__,cryptopia_api,crypto-bridge,config'.find(op) < 0]
print(' '.join(operations))
