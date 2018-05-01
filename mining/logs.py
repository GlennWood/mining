import os
import subprocess
import start

def process(self, config, coin):
    global TAIL_LOG_FILES
    if config.VERBOSE: print(__name__+".process("+coin['COIN']+")")

    '''
TODO Idea - filter special grep's to STDERR, e.g. Claymore's restarting message(s) and its warning, here,
         got incorrect share. If you see this warning often, make sure you did not overclock it too much!
         WATCHDOG: GPU 4 hangs in OpenCL call, exit
         NVML: cannot get current temperature, error 15
         Miner cannot initialize for 5 minutes, need to restart miner!
        /opt/suprminer/ccminer RVN: Cuda error in func 'cuda_check_cpu_setTarget' at line 41 : an illegal memory access was encountered.

    FIXME: This is too slow, needs a restart
     m  18:45:25|ethminer|  Speed 319.85 Mh/s    gpu/0 26.58  gpu/1 26.67  gpu/2 26.76  gpu/3 26.67  gpu/4 26.76  gpu/5 26.76  gpu/6 26.49  gpu/7 26.58  gpu/8 26.58  gpu/9 26.67  gpu/10 26.76  gpu/11 26.58  [A203+3:R0+0:F0] Time: 00:40
    
    '''

    # We have this way of handing all this off to SystemD ...
    miner = coin['MINER']
    client = None
    if miner in config.SHEETS['Clients']:
        client = config.SHEETS['Clients'][miner]
        miner = client['EXECUTABLE']
    if miner in start.MINER_TO_BINARY: miner = start.MINER_TO_BINARY[miner]
    if miner.endswith('.service'):
        TAIL_LOG_FILES = ['/bin/journalctl',  '-f']
    else:
        for ext in ['.log','.err','.out']:
            logName = '/var/log/mining/'+config.WORKER_NAME+ext
            if os.path.isfile(logName):
                TAIL_LOG_FILES.append(logName)
    return 0

def initialize(self, config, coin):
    # TODO Idea - if ALL_COINS, select logs of running miners only
    global TAIL_LOG_FILES
    TAIL_LOG_FILES = ['/usr/bin/tail', '-f']
    if config.VERBOSE: print(__name__+".initialize("+coin['COIN']+")")
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    global TAIL_LOG_FILES
    if config.VERBOSE: print(__name__+".finalize("+coin['COIN']+")")
    if len(TAIL_LOG_FILES) is 0: return config.ALL_MEANS_ONCE
    if config.DRYRUN:
        print ' '.join(TAIL_LOG_FILES)
    else:
        try:
            subprocess.call(TAIL_LOG_FILES)
        except KeyboardInterrupt:
            if config.VERBOSE: print 'exit: miners logs '+' '.join(config.arguments['COIN'])

    return config.ALL_MEANS_ONCE
