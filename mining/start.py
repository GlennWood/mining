import os
import re
import sys

MINER_TO_CHDIR = {
    'optiminer-zcash': '/opt/optiminer-zcash',
    'nsgminer': '/opt/nsgminer',
    'ccminer-KlausT': '/opt/ccminer-KlausT',
    'optiminer-equihash': '/opt/optiminer/optiminer-equihash',
    'zecminer64': '/opt/zecminer64',
    'ethdcrminer64': '/opt/ethdcrminer64'
    }

MINER_TO_BINARY = {
    'ccminer-KlausT': 'ccminer'
}

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['COIN']+")")

    Clients = config.client_dict
    arguments = config.arguments

    miner = coin['MINER']
    options = ''
    if 'OPTIONS' in coin and coin['OPTIONS'] != None:
        options = coin['OPTIONS']

    ### Translate built-in miner operations (if coin['MINER'] is a mnemonic)
    cdDir = None
    client = None
    if miner in Clients:
        client = Clients[miner]
        miner = client['EXECUTABLE']
        if options is '' and client['OPTIONS'] != None: options = client['OPTIONS']
        if client['CHDIR'] != None: cdDir = client['CHDIR']
    if cdDir is None:
        for miner_key in MINER_TO_CHDIR:
            if miner.find(miner_key) >= 0:
                cdDir = MINER_TO_CHDIR[miner_key]
                break
    if miner in MINER_TO_BINARY: miner = MINER_TO_BINARY[miner]
    if not miner.startswith('/') and not miner.startswith('.'): miner = './' + miner

    # Replace $URL_PORT, and/or $URL and $PORT, with configured value(s)
    options = options.replace('$URL_PORT', coin['URL_PORT'])
    regex = re.compile(r'(.*)[:]([0-9]{4,5})', re.DOTALL)
    match = regex.match(coin['URL_PORT'])
    if match != None:
        options = options.replace('$URL', match.group(1)).replace('$PORT', match.group(2))

    # Replace $USER_PSW, and/or $USER and $PSW, with configured value(s)
    USER_PSW = coin['USER_PSW'].split(':')
    if len(USER_PSW) > 1:
        options = options.replace('$USER', USER_PSW[0]).replace('$PASSWORD', USER_PSW[1])
    else:
        options = options.replace('$PASSWORD', coin['USER_PSW'])

    # Replace $WALLET and $COIN with configured values
    options = options.replace('$WALLET', coin['WALLET']).replace('$COIN', coin['COIN'])

    # Replace $WORKER_NAME with calculated value
    WORKER_NAME = coin['COIN'].upper() + '-miner'
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

    # TODO: Convert --platform into each miner's format for their parameter
    if arguments['--platform']:
        PLATFORM_ARG = '-platform ' + arguments['--platform']
    else:
        PLATFORM_ARG = ''

    options = options.replace('$PLATFORM', PLATFORM_ARG)

    # Transpose Environment settings to a environment map
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
        miner = './' + minerDir.pop()
        cdDir = '/'.join(minerDir)
    if config.DRYRUN:
        if environment is None: environment = ''
        if miner is None: miner = '<None>'
        if options is None: options = '<None>'
        cmd = 'cd '+cdDir+' ; '+environment+' nohup '+miner+' '+options+' >/var/log/mining/'+WORKER_NAME+'.log' + ' 2>/var/log/mining/'+WORKER_NAME+'.err' + ' &'

        print cmd
        return 0

    cmd = 'cd '+cdDir+' ; '+environment+' nohup '+miner+' '+options+' >/var/log/mining/'+WORKER_NAME+'.log' + ' 2>/var/log/mining/'+WORKER_NAME+'.err' + ' &'
    try:
        # Fork this!
        newpid = os.fork()
        if newpid == 0: return 0

        # Make sure we're in the right working directory for the miner
        if cdDir != None: os.chdir(cdDir)
        
        try:
            os.setsid()
        except OSError as ex:# 'fork of './ccminer' failed: 1 (Operation not permitted)' 
            newpid = newpid#  due to python's exception when you are already the group-leader ... 
        os.umask(0)
             
        os.system(cmd)

    except OSError, ex:
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
