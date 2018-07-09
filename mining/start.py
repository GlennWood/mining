from __future__ import print_function
import sys
import time
import overclock
import restart
import os

### FIXME: 'start' does not recognize PLATFORM 'BTH' or empty as acceptable for PLATFORM=NVI

MINER_TO_CHDIR = {
    'optiminer-zcash': '/opt/optiminer-zcash',
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

    miner = minerName = coin['MINER']
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
            print("Mining client "+client['MNEMONIC']+" does not work on this $PLATFORM="+os.getenv('PLATFORM','NONE'), file=sys.stderr)
            sys.exit(3)

        miner = client['EXECUTABLE']
        if options is '' and client['OPTIONS'] != None: options = client['OPTIONS']
        if client['CHDIR'] != None: cdDir = client['CHDIR']

        environment = client['ENVIRONMENT'] + ' ' + coin['ENVIRONMENT']
    else:
        environment = coin['ENVIRONMENT']


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
            print(cmd)
        else:
            os.system(cmd)
        return 0

    # Replace $VARNAME, and <VARNAME>, variables with configured value(s)
    WORKER_NAME = config.SHEETS['CoinMiners'][coinKey]['WORKER_NAME'] = config.workerName(coinKey)
    options = config.substitute(coinKey, options)
    
    # Replace $WALLET and $COIN with configured values
    #options = options.replace('$WALLET', coin['WALLET']).replace('$COIN', coin['COIN'])

    # Replace $GPUS, etc., with option (from command line argument) appropriate to mining client
    gpus = ''
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
    options = options.replace('$GPUS', gpus).replace('<GPUS>', gpus)

    # TODO: Convert --platform into each miner's format for their parameter
    # FIXME: fix this in config.substitution() ...
    if arguments['--platform']:
        PLATFORM_ARG = '-platform ' + arguments['--platform']
    else:
        PLATFORM_ARG = ''

    options = options.replace('$PLATFORM', PLATFORM_ARG)

    # Transpose Environment settings to a environment map
    environ = {}
    unbuffer = ''
    if environment != None and len(environment) > 0:
        for envKeyVal in environment.split():
            if envKeyVal.find('=') < 0:
                envKeyVal = [envKeyVal, '1']
            else:
                envKeyVal = envKeyVal.split('=',1)
            if envKeyVal[0] == 'UNBUFFER':
                unbuffer = 'unbuffer '
            else:
                environ[envKeyVal[0]] = envKeyVal[1]
    environment = ''
    for key in environ:
        environment += ' ' + key + '=' + environ[key]

    if cdDir is None:
        minerDir = miner.split('/')
        if len(minerDir) > 1:
            miner = './' + minerDir.pop()
            cdDir = '/'.join(minerDir)

    cmd = '' # don't think too hard about these lines; they just make DRYRUN look prettier
    if cdDir: cmd = 'cd '+cdDir+' ; '
    if environment != '': cmd += environment + ' '
    cmd += 'nohup ' + unbuffer + miner + ' ' + options
    if not config.DRYRUN or config.VERBOSE: cmd += ' >/var/log/mining/'+WORKER_NAME+'.log' + ' 2>/var/log/mining/'+WORKER_NAME+'.err' + ' &'
    if config.DRYRUN:
        restart.write_latest_start_cmd(config, cmd, WORKER_NAME)
        print(cmd)
        return 0

    # Set overclocking for this coin
    if not config.QUICK:
        overclock.initialize(self, config, coin)
        overclock.process(self, config, coin, quiet=True)
        overclock.finalize(self, config, coin)

    try:
        if config.VERBOSE: print(cmd)
        # Fork this!
        newpid = os.fork()
        if newpid != 0:
            print("Started mining "+coinKey+" with "+minerName+" at " + config.substitute(coinKey, '$URL_PORT'))
            if len(config.OPS) > 1:  # If there are more OPs on the command line, it might be
                time.sleep(1.0) # prudent to wait a second before proceeding with them.
            return 0 
        config.I_AM_FORK = True # Do not loop to any more OPs in this fork.

        # Make sure we're in the right working directory for the miner
        if cdDir != None and cdDir.strip() != '': 
            try:
                os.chdir(cdDir)
            except OSError as ex:
                print("change directory to '"+cdDir+"' failed: %d (%s)" % (ex.errno, ex.strerror), file=sys.stderr)
                sys.exit(ex.errno)
        
        try: os.setsid()
        except OSError as ex:# 'fork of './ccminer' failed: 1 (Operation not permitted)' 
            newpid = newpid#  due to python's exception when you are already the group-leader ... 
        os.umask(0)
        
        restart.write_latest_start_cmd(config, cmd, WORKER_NAME)
        os.system(cmd)

    except SystemExit as ex:
        print("Exiting")
    except OSError as ex:
        print("fork of '"+miner+"' failed: %d (%s)" % (ex.errno, ex.strerror), file=sys.stderr)
        sys.exit(1)
    except:
        ex = sys.exc_info()[0]
        print( "Unknown exception in fork: "+str(ex) )


def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['COIN']+")")
    return 0

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['COIN']+")")
    return 0
