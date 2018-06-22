from __future__ import print_function
import os
import sys
import subprocess
import start
import status
import time
import re
import yaml

LOGS_CONFIG = {'SCOPES': { } }

def process(self, config, coin):
    global TAIL_LOG_FILES

    '''
    TODO Idea - filter special grep's to STDERR, e.g. Claymore's restarting message(s) and its warning, here,
         got incorrect share. If you see this warning often, make sure you did not overclock it too much!
         WATCHDOG: GPU 4 hangs in OpenCL call, exit
         NVML: cannot get current temperature, error 15
         Miner cannot initialize for 5 minutes, need to restart miner!
        /opt/suprminer/ccminer RVN: Cuda error in func 'cuda_check_cpu_setTarget' at line 41 : an illegal memory access was encountered.

    FIXME: This is too slow, needs a restart
     m  18:45:25|ethminer|  Speed 319.85 Mh/s    gpu/0 26.58  gpu/1 26.67  gpu/2 26.76  gpu/3 26.67  gpu/4 26.76  gpu/5 26.76  gpu/6 26.49  gpu/7 26.58  gpu/8 26.58  gpu/9 26.67  gpu/10 26.76  gpu/11 26.58  [A203+3:R0+0:F0] Time: 00:40
    
    FIXME: RVN keeps failing this way
    rvn.log - [2018-06-22 14:08:59] GPU #2: an illegal memory access was encountered
    rvn.err - Cuda error in func 'cuda_check_cpu_setTarget' at line 41 : an illegal memory access was encountered.
    '''
        
    if isinstance(coin, list):
        # This happens with 'miners swap,logs old-coin:new-coin'
        coin = coin[1]
        time.sleep(0.1)
    miner = coin['MINER']

    client = None
    if miner in config.SHEETS['Clients']:
        client = config.SHEETS['Clients'][miner]
        miner = client['EXECUTABLE']
    if miner in start.MINER_TO_BINARY: miner = start.MINER_TO_BINARY[miner]
    
    # If no coins on command line, then list only those of currently running miners
    if config.ALL_COINS:
        pinfos = status.get_status(config.arguments['COIN'])
        if pinfos is None or len(pinfos) == 0:
            print("No processes are mining "+','.join(config.arguments['COIN'])+'.',file=sys.stderr)
            return config.ALL_MEANS_ONCE
        for pinfo in pinfos:
            WORKER_NAME = config.workerName(pinfo['coin'])
            for ext in ['.log','.err','.out']:
                logName = '/var/log/mining/'+WORKER_NAME+ext
                if os.path.isfile(logName):
                    TAIL_LOG_FILES.append(logName)
        return config.ALL_MEANS_ONCE


    if miner.endswith('.service'):
        TAIL_LOG_FILES = ['/bin/journalctl',  '-f', '--utc']
        # The '--utc' makes len(TAIL_LOG_FILES)>2 so it doesn't get passed over in finalize()
    else:
        for ext in ['.log','.err','.out']:
            logName = '/var/log/mining/'+config.workerName(coin['COIN'])+ext
            if os.path.isfile(logName):
                TAIL_LOG_FILES.append(logName)
            else:
                if config.VERBOSE:
                    print("There is no log file named '"+logName+"'")
    return 0

def load_logs_config():
    global LOGS_CONFIG
    logs_config_filename = "/opt/mining/conf/logs.yml"
    if os.path.isfile(logs_config_filename):
        with open(logs_config_filename, 'r') as stream:
            try:
                LOGS_CONFIG = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

def initialize(self, config, coin):
    global TAIL_LOG_FILES
    TAIL_LOG_FILES = ['/usr/bin/tail', '-f']
    load_logs_config()
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    global TAIL_LOG_FILES
    if len(TAIL_LOG_FILES) <= 2:
        return config.ALL_MEANS_ONCE

    try:
        if config.SCOPE is None or config.SCOPE == '':
            scopes = None
        elif config.SCOPE in LOGS_CONFIG['SCOPES']:
            scopes = LOGS_CONFIG['SCOPES'][config.SCOPE]
        elif config.SCOPE == 'speed':
            scopes = [ r'.*(Total Speed[^,]*)', r'GPU #[0-9.,]*: [0-9.,]* [GMKgmk][Hh]z' , r'(GPU #[0-9]*: [^,]*, [0-9.,]* [GMKgmk][Hh]/s)' ]
        #elif config.SCOPE == 'temp':
        #    scopes = [ r' t=([0-9]*)C' ]
        else:
            scopes = [ config.SCOPE ]
    except:
        print(sys.exc_info())
        return config.ALL_MEANS_ONCE

    if config.DRYRUN:
        print(' '.join(TAIL_LOG_FILES))
    else:
        try:
            proc = subprocess.Popen(TAIL_LOG_FILES, stdout=subprocess.PIPE)
            while True:
                line = proc.stdout.readline().decode().rstrip()
                if scopes is None:
                    print(line)
                else:
                    for scope in scopes:
                        match = re.findall(scope, line)
                        if match and len(match) > 0:
                            print(','.join(match))
        except KeyboardInterrupt:
            if config.VERBOSE: print('KeyboardInterrupt: miners logs '+' '.join(config.arguments['COIN']))
        except:# os.ProcessLookupError: # strangely, subprocess fails this way after Ctrl-C sometimes; squelch annoying message.
            if config.VERBOSE: print('ProcessLookupError (during KeyboardInterrupt is OK): miners logs '+' '.join(config.arguments['COIN']))

    return config.ALL_MEANS_ONCE
