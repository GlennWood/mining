import os
import re
import sys
from pip._vendor.distlib.util import chdir

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['Coin']+")")

    Clients = config.client_dict
    arguments = config.arguments

    miner = coin['Miner']
    options = ''
    if 'Options' in coin and coin['Options'] != None:
        options = coin['Options']

    ### Translate built-in miner operations (if coin['Miner'] is a mnemonic)
    cdDir = None
    client = None
    if miner in Clients:
        client = Clients[miner]
        miner = client['Executable']
        if options is '' and client['Options'] != None:
            options = client['Options']

    # Replace $URL_PORT, and/or $URL and $PORT, with configured value(s)
    options = options.replace('$URL_PORT', coin['UrlPort'])
    regex = re.compile(r'(.*)[:]([0-9]{4,5})', re.DOTALL)
    match = regex.match(coin['UrlPort'])
    if match != None:
        options = options.replace('$URL', match.group(1)).replace('$PORT', match.group(2))

    # Replace $USER_PSW, and/or $USER and $PSW, with configured value(s)
    USER_PSW = coin['UserPassword'].split(':')
    if len(USER_PSW) > 1:
        options = options.replace('$USER', USER_PSW[0]).replace('$PASSWORD', USER_PSW[1])
    else:
        options = options.replace('$PASSWORD', coin['UserPassword'])

    # Replace $WALLET and $COIN with configured values
    options = options.replace('$WALLET', coin['Wallet']).replace('$COIN', coin['Coin'])

    # Replace $WORKER_NAME with calculated value
    WORKER_NAME = coin['Coin'].upper() + '-miner'
    options = options.replace('$WORKER_NAME', WORKER_NAME)

    # Replace $GPUS, etc., with option (from command line argument) appropriate to mining client
    if arguments['--gpus']:
        GPUS_WC = arguments['--gpus']
        if miner == 'ethdcrminer64' or miner == 'zecminer64':
            gpus = '-di ' + GPUS_WC.replace(',','')
        elif miner.find('ewbf'):
            gpus = '--cuda_devices ' + GPUS_WC.replace(',', ' ')
        elif miner.find('optiminer-equihash'):
            GPUS_LIST = GPUS_WC.split(',')
            gpus = '-d '+ '-d '.join(GPUS_LIST)
        options = options.replace('$GPUS', gpus)
    else:
        options = options.replace('$GPUS', '')

    # Some miners require cd: e.g., optiminer-equihash, zecminer64, ethdcrminer64
    # We also convert --platform into each miner's format for their parameter
    if arguments['--platform']:
        PLATFORM_ARG = '-platform ' + arguments['--platform']
    else:
        PLATFORM_ARG = ''
    if miner == 'ethdcrminer64':
        if cdDir is None: cdDir = '/opt/ethdcrminer64'
        miner = './'+miner
    elif miner.find('zecminer64') >= 0:
        if cdDir is None: cdDir = '/opt/zecminer64'
        miner = './'+miner
    elif miner.find('optiminer-equihash') >= 0:
        if cdDir is None: cdDir = '/opt/optiminer/optiminer-equihash'
        miner = './'+miner
        PLATFORM_ARG = ''
    elif miner.find('ccminer-KlausT') >= 0:
        if cdDir is None: cdDir = '/opt/ccminer-KlausT'
        miner = miner.replace('ccminer-KlausT', './ccminer')
    elif miner.find('nsgminer') >= 0:
        if cdDir is None: cdDir = '/opt/nsgminer'
        miner = './'+miner
    elif miner.find('optiminer-zcash') >= 0:
        if cdDir is None: cdDir = '/opt/optiminer-zcash'
        miner = './'+miner
        #./optiminer-zcash -s us-east.equihash-hub.miningpoolhub.com:20570 -u albokiadt.ZEC-miner -p RLaA58k3PmwjcLGZ 
    else:
        PLATFORM_ARG = ''
    options = options.replace('$PLATFORM', PLATFORM_ARG)


    # Transpose Environment settings to a environment map
    environment = {}
    if coin['Environment'] != None:
        for envKeyVal in coin['Environment'].split():
            envKeyVal = envKeyVal.split('=',1)
            environment[envKeyVal[0]] = envKeyVal[1]


    # And now we go for it, dryrun, or fork and exec
    # We could have used just os.subprocess(nohup...), but consider the following scenario:
    #
    #     # miners start,logs eth
    #
    # You watch the logs for a bit, everything is fine, then you ctrl-C and move on to other things.
    #
    # Hours later you learn that the ctrl-C killed the miner!
    #
    # 'nohup' will protect you from the simple exit of the parent, but not from ctrl-C.
    #
    # So here we go ...
    if config.DRYRUN:
        print 'cd '+cdDir+' ; nohup '+miner+' '+options+' >/var/log/mining/'+WORKER_NAME+'.log' + ' 2>/var/log/mining/'+WORKER_NAME+'.err' + ' &'
        return 0
    else:
        try:
            newpid = os.fork()
            if newpid == 0:
                return 0
            else:
                if client != None and 'chdir' in client and client['chdir'] != None: os.chdir(cdDir)

                try:
                    os.setsid()
                except OSError, e:# 'fork of './ccminer' failed: 1 (Operation not permitted)' 
                    newpid = newpid#  due to python's exception when you are already the group-leader ... 
                os.umask(0)
    
                open('/var/log/mining/'+WORKER_NAME+'.in', 'w').close()
                sys.stdin  = open('/var/log/mining/'+WORKER_NAME+'.in',  'r')
                sys.stdout = open('/var/log/mining/'+WORKER_NAME+'.out', 'w')
                sys.stderr = open('/var/log/mining/'+WORKER_NAME+'.err', 'w')
                # Ref: https://stackoverflow.com/questions/8500047/how-to-inherit-stdin-and-stdout-in-python-by-using-os-execv/8500169#8500169
                os.dup2(sys.stdin.fileno(),  0)
                os.dup2(sys.stdout.fileno(), 1)
                os.dup2(sys.stderr.fileno(), 2)
    
                os.execve(miner, options.split(), environment)
                # and we're done; execve does not return
    
        except OSError, e:
            print >> sys.stderr, "fork of '"+miner+"' failed: %d (%s)" % (e.errno, e.strerror)
            sys.exit(1)


def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['Coin']+")")

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['Coin']+")")
    return 0
