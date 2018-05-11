import os
import sys
import socket
import time

'''
FIXME:

05:33:47|stratum |  Received new job 6e98a77c, from daggerhashimoto.usa.nicehash.com
  05:33:49|cuda-6  |  Fatal GPU error: CUDA error in func search at line 504 unspecified launch failure
  05:33:49|cuda-6  |  Terminating.
  05:33:49|cuda-11 |  Fatal GPU error: CUDA error in func search at line 504 unspecified launch failure
root@rig-19X:/opt/ethminer/build# 
root@rig-19X:/opt/ethminer/build# ethminer -SP 2 -U -S daggerhashimoto.usa.nicehash.com:3353 -O 346u4oMvACtZQK9RASzcgYoZwX4JaAd3Pi.NICEHASH-ETHASH-miner:x

Ctrl-C ->  '16:54:03|ethminer|  Shutting down miners...'
'''


MINER_TO_CHDIR = {
    'optiminer-zcash': '/opt/optiminer-zcash',
    #'nsgminer': '/opt/nsgminer',
    'ccminer-KlausT': '/opt/ccminer-KlausT',
    'optiminer-equihash': '/opt/optiminer/optiminer-equihash',
    'zecminer64': '/opt/zecminer64',
    'ethdcrminer64': '/opt/ethdcrminer64'
    }

MINER_TO_BINARY = {
    'ccminer-KlausT': '/opt/ccminer-KlausT/ccminer'
}

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['COIN']+")")
    arguments = config.arguments

    Clients = config.SHEETS['Clients']
    coinKey = coin['COIN'].upper()

    miner = coin['MINER']
    options = ''
    if 'OPTIONS' in coin and coin['OPTIONS'] != None:
        options = coin['OPTIONS']

    ### Translate built-in miner operations (if coin['MINER'] is a mnemonic)
    cdDir = None
    client = None
    if miner in Clients:
        client = Clients[miner]

        platform = client['PLATFORM']
        if platform != 'BTH' and platform != os.getenv('PLATFORM','BTH'):
            print >>sys.stderr, "Mining client "+client['MNEMONIC']+" does not work on this $PLATFORM="+os.getenv('PLATFORM','NONE')
            sys.exit(3)

        miner = client['EXECUTABLE']
        if options is '' and client['OPTIONS'] != None: options = client['OPTIONS']
        if client['CHDIR'] != None: cdDir = client['CHDIR']

    if cdDir is None:
        for miner_key in MINER_TO_CHDIR:
            if miner.find(miner_key) >= 0:
                cdDir = MINER_TO_CHDIR[miner_key]
                break

    if miner in MINER_TO_BINARY: miner = MINER_TO_BINARY[miner]

    # We have this way of handing all this off to SystemD ...
    if miner.endswith('.service'):
        miner = miner.replace('.service','')
        cmd = 'sudo service '+miner+' start'
        if config.DRYRUN:
            print cmd
        else:
            os.system(cmd)
        return 0

    # Replace $VARNAME, and <VARNAME>, variables with configured value(s)
    hostN = socket.gethostname()
    WORKER_NAME = config.SHEETS['CoinMiners'][coinKey]['WORKER_NAME'] = coinKey + '-miner-' + hostN[len(hostN)-1]
    options = config.substitute(coinKey, options)
    
    # Replace $WALLET and $COIN with configured values
    #options = options.replace('$WALLET', coin['WALLET']).replace('$COIN', coin['COIN'])

    # Replace $GPUS, etc., with option (from command line argument) appropriate to mining client
    if arguments['--gpus']:
        gpus = ''
        GPUS_WC = arguments['--gpus']
        GPUS_LIST = GPUS_WC.split(',')
        if miner.find('ethdcrminer64') >= 0 or miner.find('zecminer64') >= 0:
            gpus = '-di ' + GPUS_WC.replace(',','')
        elif miner.find('ewbf') >= 0 or (cdDir != None and cdDir.find('ewbf') >= 0):
            gpus = '--cuda_devices ' + GPUS_WC.replace(',', ' ')
        elif miner.find('nheqminer') >= 0:
            gpus = '-cd '+ ' '.join(GPUS_LIST)
        elif miner.find('optiminer-equihash') >= 0:
            gpus = '-d '+ '-d '.join(GPUS_LIST)
        elif miner.find('ccminer') >= 0 or miner.find('sgminer') >= 0:
            gpus = '-d '+ GPUS_WC
        elif miner.find('bminer') >= 0:
            # TODO: bminer apparently runs on a max of 4 gpus?
            gpus = '-devices '+ GPUS_WC
        options = options.replace('$GPUS', gpus)
    else:
        options = options.replace('$GPUS', '')

    # TODO: Convert --platform into each miner's format for their parameter
    # FIXME: fix this in config.substitution() ...
    if arguments['--platform']:
        PLATFORM_ARG = '-platform ' + arguments['--platform']
    else:
        PLATFORM_ARG = ''

    options = options.replace('$PLATFORM', PLATFORM_ARG)

    # Transpose Environment settings to a environment map
    # FIXME: SHEET['Clients'] has multiple rows per ENVIRONMENT - needs coalescing somehow
    environ = {}
    environment = coin['ENVIRONMENT']
    if environment != None and len(environment) > 0:
        for envKeyVal in environment.split():
            envKeyVal = envKeyVal.split('=',1)
            environ[envKeyVal[0]] = envKeyVal[1]
    else:
        environment = ''

    if cdDir is None:
        minerDir = miner.split('/')
        if len(minerDir) > 1:
            miner = './' + minerDir.pop()
            cdDir = '/'.join(minerDir)

    cmd = '' # don't think too hard about these lines; they just make DRYRUN look prettier
    if cdDir: cmd = 'cd '+cdDir+' ; '
    if environment != '': cmd += environment + ' ' 
    cmd += 'nohup ' + miner + ' ' + options
    if not config.DRYRUN or config.VERBOSE: cmd += ' >/var/log/mining/'+WORKER_NAME+'.log' + ' 2>/var/log/mining/'+WORKER_NAME+'.err' + ' &'
    if config.DRYRUN:
        print cmd
        return 0

    try:
        if config.VERBOSE: print cmd
        # Fork this!
        newpid = os.fork()
        if newpid != 0: 
            time.sleep(1.0)
            return 0
        config.I_AM_FORK = True # Do not loop to any more OPs in this fork.

        # Make sure we're in the right working directory for the miner
        if cdDir != None and cdDir.strip() != '': 
            try:
                os.chdir(cdDir)
            except OSError, ex:
                print >> sys.stderr, "change directory to '"+cdDir+"' failed: %d (%s)" % (ex.errno, ex.strerror)
                sys.exit(ex.errno)
        
        try: os.setsid()
        except OSError as ex:# 'fork of './ccminer' failed: 1 (Operation not permitted)' 
            newpid = newpid#  due to python's exception when you are already the group-leader ... 
        os.umask(0)
             
        os.system(cmd)

    except SystemExit as ex:
        print "Exiting"
    except OSError as ex:
        print >> sys.stderr, "fork of '"+miner+"' failed: %d (%s)" % (ex.errno, ex.strerror)
        sys.exit(1)
    except:
        ex = sys.exc_info()[0]
        print ( ex )


def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['COIN']+")")
    return 0

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['COIN']+")")
    return 0
