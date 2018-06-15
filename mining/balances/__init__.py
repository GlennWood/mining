from __future__ import print_function
### Ref: http://python-future.org/compatible_idioms.html
from builtins import range
import subprocess
import json
import time
import sys
import os
import pycurl
import yaml
from balances.cryptopia_api import Api
import gdax
from balances.bleutradeapi import Bleutrade

# These sources have their own reader, instead of 'curl' for all others
OWN_READER = {
    'bit-shares': 'bit-shares',
    'cryptopia': 'cryptopia',
    'gdax': 'gdax'
}

def process(self, config, coin):

    SOURCES_YML = load_config()

    if config.ALL_COINS: # meaning there was no command-line parameter following the OP 'balances'
        if config.SCOPE:
            scope = config.SCOPE.upper()
            if scope in SOURCES_YML['SCOPING']:
                Sources = (SOURCES_YML['SCOPING'][scope])
            else:
                print("'%s' not found in SCOPING of 'balances/sources.yml'."%(scope))
                return config.ALL_MEANS_ONCE
        else:
            Sources = sorted(SOURCES_YML['SOURCES'].keys())
    else:
        Sources = [ source.upper() for source in config.arguments['COIN'] ]

    miners_user_ssh = '/home/'+os.getenv('MINERS_USER')+'/.ssh/mining-keys/'
    UNIMINING_THROTTLE=False

    for source in Sources:
        if not source in SOURCES_YML['SOURCES']:
            print("'"+source+"' is an unknown source, expecting one of "+','.join(sorted(SOURCES_YML['SOURCES'].keys())),file=sys.stderr)
            continue
        RETRYING_IS_OK = True
        KEYBOARD_INTERRUPT = False

        print(source)
        while RETRYING_IS_OK and not KEYBOARD_INTERRUPT:
            RETRYING_IS_OK = False
            for ticker in sorted(SOURCES_YML['SOURCES'][source]):
                if KEYBOARD_INTERRUPT:
                    continue

                if source == 'UNIMINING' and UNIMINING_THROTTLE:
                    try:
                        for t in range(0,65):
                            print('\rPausing to accommodate unimining\'s throttling (use "-q" to bypass this)...'+str(65-t)+' ',end='',file=sys.stderr),;sys.stderr.flush()
                            time.sleep(1)
                    except KeyboardInterrupt:
                        if config.VERBOSE: print('KeyboardInterrupt: miners balances '+' '.join(config.arguments['COIN']))
                        KEYBOARD_INTERRUPT = True
                        RETRYING_IS_OK = False
                    print ('\r                                                                                 \r',end='',file=sys.stderr),;sys.stderr.flush()
                    if KEYBOARD_INTERRUPT:
                        print('  '+ticker+' KeyboardInterrupt')
                        continue
                UNIMINING_THROTTLE=False
            
                balanceUrls = SOURCES_YML['SOURCES'][source][ticker]
                if not isinstance(balanceUrls, list):
                    balanceUrls = [ balanceUrls ]
                keyFile = miners_user_ssh + source.lower()
                if ticker != 'all':
                    keyFile += '-' + ticker.lower()
                secrets_json = None
                try:
                    with open(keyFile+'.key') as secrets:
                        secrets_json = json.load(secrets)
                        secrets.close()
                        for idx in range(len(balanceUrls)):
                            for key in secrets_json:
                                if balanceUrls[idx]:
                                    balanceUrls[idx] = balanceUrls[idx].replace('$'+key.upper(),secrets_json[key])
                except IOError as ex:
                    print("  "+ticker+" Cannot read key file for "+source+", "+str(ex), file=sys.stderr)
                    continue
                
                balanceUrl = balanceUrls[0]
                if config.VERBOSE and balanceUrl and balanceUrl not in OWN_READER:
                    print ('URL: '+balanceUrl)

                jsonStr = '<NaS>'
                if balanceUrl and balanceUrl not in OWN_READER:
                    jsonObj = getUrlToJsonObj(config, balanceUrl, source, ticker, miners_user_ssh)
            
                ### ####################################################### ###
                # Parse the downloaded data according to each pool's format.
                if source == 'BLEUTRADE':
                    if ticker == 'all':
                        currencies = ticker;
                    else:
                        currencies = [ ticker ]
                    jsonRslt = Bleutrade(secrets_json['api_key'], secrets_json['api_secret']).get_balances(currencies)
                    for coin in jsonRslt['result']:
                        balance = float(coin['Balance'])
                        if balance != 0 or ticker != 'all':
                            print('  '+coin['Currency']+' '+str(balance))

                elif balanceUrl == 'cryptopia':
                    api_wrapper = Api(keyFile+'.key', None)
                    
                    balances, error = api_wrapper.get_balances()
                    if error is not None:
                        print('ERROR: %s' % error, file=sys.stderr)
                    else:
                        for balance in balances:
                            if balance['Total']:
                                print('  '+balance['Symbol'] + " " + str(balance['Total']))
        
                elif source == 'MININGPOOLHUB':
                    try:
                        for coin in jsonObj['getuserallbalances']['data']:
                            tot = coin['confirmed'] + coin['unconfirmed']+ coin['ae_confirmed'] + coin['ae_unconfirmed'] + coin['exchange']
                            print('  '+SOURCES_YML['COMMON_TO_SYMBOL'][coin['coin']]+' '+str(tot))            
                    except:
                        print("  ERROR: "+str(jsonObj))
          
                elif source == 'NICEHASH':
                    if 'error' in jsonObj['result']:
                        print('  BTC ERROR: %s'%(jsonObj['result']['error']))
                    else:
                        total = float(jsonObj['result']['balance_confirmed'])+float(jsonObj['result']['balance_pending'])
                        if len(balanceUrls) > 1:
                            statsObj = getUrlToJsonObj(config, balanceUrls[1], source, ticker, miners_user_ssh)
                            result = statsObj['result']
                            if 'error' in result:
                                print('  BTC stats.provider '+result['error'])
                            else:
                                total += float(statsObj['result']['stats'][0]['balance'])
                        print('  BTC %.8f'%(total))
            
                elif source == 'GDAX':
                    auth_client = gdax.AuthenticatedClient(secrets_json['api_key'], secrets_json['api_secret'], secrets_json['api_passphrase'])
                    accounts = auth_client.get_accounts()
                    for account in accounts:
                        balance = float(account['balance'])
                        print('  '+account['currency']+' '+str(balance))

                elif source == 'SUPRNOVA':
                    try:
                        data = jsonObj['getuserbalance']['data']
                        print('  '+ticker + ' ' + str(data['confirmed']+data['unconfirmed']))
                    except:
                        print('  '+ticker+' ERROR: '+str(jsonObj))
        
                elif source == 'UNIMINING':          
                    # Ref: https://www.unimining.net/api
                    if jsonObj is None:
                        if config.QUICK:
                            if not KEYBOARD_INTERRUPT:
                                print('???'+' unimining/api returned nothing; probably their throttling mechanism; quickly bypassing that balance.')
                            UNIMINING_THROTTLE=False
                        else:
                            if not KEYBOARD_INTERRUPT:
                                print('???'+' unimining/api returned nothing; probably their throttling mechanism; retrying now.')
                            RETRYING_IS_OK=True
                    else:
                        try:
                            if not config.QUICK and not KEYBOARD_INTERRUPT:
                                UNIMINING_THROTTLE=True
                            print('  '+jsonObj['currency']+' '+str(jsonObj['total']))
                        except:
                            print("  ERROR: "+jsonStr)

                elif balanceUrl == 'bit-shares':
                    balances_bit_shares(source)
            
                else:
                    print("Don't know how to process "+source+'-'+ticker+" = "+balanceUrl)
                    if config.VERBOSE: print(jsonStr)

    return config.ALL_MEANS_ONCE

### ###########################################################
# Fetch and print balances from any exchange based on bitshares.
def balances_bit_shares(source):        
    proc = subprocess.Popen(['/usr/bin/python3','/opt/mining/mining/balances/bit-shares.py', source], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = proc.communicate(None)
    if err:
        print(err,file=sys.stderr)
        return
    out = out.decode('utf-8')

    lines = out.splitlines()
    # "[0.00001017 BRIDGE.BTC, 162.1362 BRIDGE.RVN]"
    line = lines[0].replace('[','').replace(']','')
    vals = line.split(", ")
    for val in vals:
        val_coin = val.split(' ')
        value = val_coin[0]
        coin = val_coin[1].replace('BRIDGE.','')
        print('  '+coin + " " + value)

### ###############################################################################
def getUrlToJsonObj(config, balanceUrl, source, ticker='all', miners_user_ssh=None):
    jsonStr = '<NaS>'
    if balanceUrl and balanceUrl not in OWN_READER:
        proc = subprocess.Popen(['curl', balanceUrl], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        jsonStr, err = proc.communicate(None)
        jsonStr = jsonStr.decode()
        if err:
            if config.VERBOSE: print(err, file=sys.stderr)
        if config.PRINT:
            encoding = 'html'
            if 'isJson' in balanceUrl or 'miningpoolhub' in balanceUrl: encoding = 'json'
            printFilename = miners_user_ssh + source.lower()
            if ticker != 'all':
                printFilename += '-' + ticker.lower()
            printFilename += '-balances.' + encoding
            with open(printFilename, 'w') as f: f.write(jsonStr)
            print("Data downloaded from : " + balanceUrl + "\n            saved in " + printFilename)
    return json.loads(jsonStr)


### ###########################################################
def load_config():
    with open("/opt/mining/mining/balances/sources.yml", 'r') as stream:
        try:
            SOURCES_X = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)
    return SOURCES_X

### ###########################################################
def bash_completion(prev):
    SOURCES_YML = load_config()
    if prev == '--scope':
        print(' '.join(scope.lower() for scope in SOURCES_YML['SCOPING']))
    else:
        print(' '.join(source.lower() for source in SOURCES_YML['SOURCES']))

def initialize(self, config, coin):
    load_config()
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    return config.ALL_MEANS_ONCE
