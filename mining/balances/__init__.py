from __future__ import print_function
### Ref: http://python-future.org/compatible_idioms.html
from builtins import range
import subprocess
import json
import sys
import os
import re
import yaml
from balances.cryptopia_api import Api
import gdax
from balances.bleutradeapi import Bleutrade

TOTALS = { }
Config = None

def process(self, config, coin):
    global Config
    Config = config

    SOURCES_YML = load_config()
    SOURCES = SOURCES_YML['SOURCES']
    SCOPING = SOURCES_YML['SCOPING']
    OWN_READER = SOURCES_YML['OWN_READER']

    Sources = None
    if config.ALL_COINS: # meaning there was no command-line parameter following the OP 'balances'
        Sources = sorted(SOURCES.keys())
    else:
        Sources = config.arguments['COIN']

    if not Sources:
        Sources = sorted(SOURCES.keys())

    miners_user_keys = '/home/'+os.getenv('MINERS_USER',os.getenv('USER'))
    if not os.path.isdir(miners_user_keys): miners_user_keys = os.getenv('HOME')
    miners_user_keys += '/.ssh/mining-keys/'

    sourcesToDo = [ ]
    for source in Sources:
        srcs = source.split(':')
        src = srcs[0].upper()
        if not src:
            for src in SOURCES_YML['SOURCES']:
                sourcesToDo.append(src+':'+srcs[1])
        elif src not in SOURCES_YML['SOURCES']:
            if src not in SCOPING:
                print("'"+src+"' is an unknown source, expecting one of "+
                      ','.join(sorted(SOURCES.keys())) + ' or ' +
                      ','.join(sorted(SCOPING.keys())),
                      file=sys.stderr)
            else:
                for src_ in SCOPING[src]:
                    if len(srcs) > 1:
                        sourcesToDo.append(src_+':'+srcs[1])
                    else:
                        sourcesToDo.append(src_)
        else:
            sourcesToDo.append(source)

    for sourceToDo in sourcesToDo:
        srcs = sourceToDo.split(':')
        source = srcs[0].upper()
        if len(srcs) > 1:
            scopeTickers = srcs[1].upper().split(',')
        else:
            scopeTickers = None
        
        printSource = source+"\n  "
        for tickerKey in sorted(SOURCES_YML['SOURCES'][source]):
            ticker = tickerKey.split('(')
            if len(ticker) > 1:
                exchange = ticker[1].replace(')','')
            else:
                exchange = None
            ticker = ticker[0]
            if scopeTickers and ticker != 'all' and ticker not in scopeTickers:
                if config.VERBOSE: print("TICKER:"+ticker+" not in "+str(scopeTickers))
                continue

            balanceUrls = SOURCES_YML['SOURCES'][source][tickerKey]
            if not isinstance(balanceUrls, list):
                balanceUrls = [ balanceUrls ]
                
            # Get the API keys/etc. from this source/ticker's miners_user_keys file
            keyFile = miners_user_keys + source.lower()
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
                print("  "+ticker+" Cannot read key file for "+source+":"+ticker+", "+str(ex), file=sys.stderr)
                continue

            balanceUrl = balanceUrls[0]
            if config.VERBOSE and source not in OWN_READER and balanceUrl and balanceUrl not in OWN_READER:
                print ('URL: '+balanceUrl)
        
            ### ####################################################### ###
            # Parse the downloaded data according to each pool's format.
            if balanceUrl and balanceUrl.startswith('MPOS:'):# or source == 'AIKAPOOL' or source == 'SUPRNOVA':
                try:
                    url = balanceUrl.split(':',1)[1]+'/index.php?page=api&action=getuserbalance&api_key=$API_KEY&id=$API_ID' \
                                .replace('$API_ID', secrets_json['api_id']).replace('$API_KEY', secrets_json['api_key'])
                    jsonObj = getUrlToJsonObj(config, url, source, ticker)
                    data = jsonObj['getuserbalance']['data']
                    printBalance(printSource, ticker, float(data['confirmed'])+float(data['unconfirmed']))
                    printSource = '  '
                except:
                    print(printSource+ticker+' ERROR: '+str(jsonObj))
                    printSource = '  '
    
            elif source == 'ALHAFEEZ':
                print("  ALHAFEEZ is NYI")
                print(balanceUrl)
                htmlStr = getUrlToStr(config, balanceUrl)
                print(htmlStr)
                
            elif source == 'ANORAK':
                jsonStr = getUrlToStr(config, balanceUrl, source, ticker, 'jsons')
                if config.VERBOSE: print(jsonStr)

            ### Ref: https://github.com/binance-exchange/binance-official-api-docs
            elif source == 'BINANCE':
                from binance.client import Client
                client = Client(secrets_json['api_key'], secrets_json['api_secret'])
                data = client.get_asset_balance(asset=ticker)
                printBalance(printSource, data['asset'], float(data['free'])+float(data['locked']))
                printSource = '  '

            elif source == 'BLEUTRADE':
                if ticker == 'all':
                    currencies = ticker;
                else:
                    currencies = [ ticker ]
                jsonRslt = Bleutrade(secrets_json['api_key'], secrets_json['api_secret']).get_balances(currencies)
                for coin in jsonRslt['result']:
                    balance = float(coin['Balance'])
                    if balance != 0 or ticker != 'all':
                        printBalance(printSource, coin['Currency'], balance)
                        printSource = '  '

            elif balanceUrl and balanceUrl == 'cryptopia':
                api_wrapper = Api(keyFile+'.key', None)
                
                balances, error = api_wrapper.get_balances()
                if error is not None:
                    print('ERROR: %s' % error, file=sys.stderr)
                else:
                    for balance in balances:
                        if balance['Total']:
                            if not scopeTickers or balance['Symbol'] in scopeTickers:
                                printBalance(printSource, balance['Symbol'], balance['Total'])
                                printSource = '  '

            elif source == 'MININGPOOLHUB':
                try:
                    jsonObj = getUrlToJsonObj(config, balanceUrl, source, ticker)
                    for coin in jsonObj['getuserallbalances']['data']:
                        tot = coin['confirmed'] + coin['unconfirmed']+ coin['ae_confirmed'] + coin['ae_unconfirmed'] + coin['exchange']
                        tckr = SOURCES_YML['COMMON_TO_SYMBOL'][coin['coin']]
                        if not scopeTickers or tckr in scopeTickers:
                            printBalance(printSource,tckr, tot)
                            printSource = '  '
                except json.decoder.JSONDecodeError as ex:
                    print(ex,file=sys.stderr)
                except:
                    print("  ERROR: "+str(jsonObj))
      
            elif source == 'NICEHASH':
                if not scopeTickers or 'BTC' in scopeTickers:
                    try:
                        jsonObj = getUrlToJsonObj(config, balanceUrl, source, ticker)
                        if 'error' in jsonObj['result']:
                            print('  BTC ERROR: %s'%(jsonObj['result']['error']))
                        else:
                            total = float(jsonObj['result']['balance_confirmed'])+float(jsonObj['result']['balance_pending'])
                            if len(balanceUrls) > 1:
                                statsObj = getUrlToJsonObj(config, balanceUrls[1], source, ticker)
                                result = statsObj['result']
                                if 'error' in result:
                                    print('  BTC stats.provider '+result['error'])
                                else:
                                    total += float(statsObj['result']['stats'][0]['balance'])
                            printBalance(printSource, 'BTC', total)
                            printSource = '  '
                    except json.decoder.JSONDecodeError as ex:
                        print(ex,file=sys.stderr)

            elif source == 'GDAX':
                auth_client = gdax.AuthenticatedClient(secrets_json['api_key'], secrets_json['api_secret'], secrets_json['api_passphrase'])
                accounts = auth_client.get_accounts()
                if 'message' in accounts:
                    print(accounts, file=sys.stderr)
                else:
                    for account in accounts:
                        if not scopeTickers or account['currency'] in scopeTickers:
                            balance = float(account['balance'])
                            printBalance(printSource, account['currency'], balance)
                            printSource = '  '

            elif balanceUrl and balanceUrl == 'bit-shares':
                balances_bit_shares(source, scopeTickers)
        
            elif balanceUrl and balanceUrl.startswith('yiimp:'): # aka UNIMINING, ZPOOL
                # Ref: https://www.unimining.net/api
                try:
                    url = balanceUrl.split(':',1)[1]+'/api/walletEx?address=$API_ID'.replace("$API_ID", secrets_json['api_id'])
                    jsonObj = getUrlToJsonObj(config, url, source, ticker)
                    printBalance(printSource, ticker, jsonObj['total'])
                    printSource = '  '
                except json.decoder.JSONDecodeError as ex:
                    # unimining/api returned nothing; probably their throttling mechanism; let's read it from the WebUI
                    url = balanceUrl.split(':',1)[1]+'/site/wallet_results?address=$API_ID&showdetails=1'.replace("$API_ID", secrets_json['api_id'])
                    webHtml = getUrlToStr(config, url, source, ticker)
                    if ticker in SOURCES_YML['SYMBOL_TO_COMMON']:
                        tckr = SOURCES_YML['SYMBOL_TO_COMMON'][ticker]
                    else:
                        tckr = ticker
                    regex = re.compile('.*?Total Earned.*?([0-9]*[.][0-9]*) '+tckr+'.*')
                    match = regex.match(webHtml)
                    if match:
                        balance = match.group(1)
                        printBalance(printSource, ticker, float(balance))
                        printSource = '  '

            else:
                print("Don't know how to process "+source+'-'+ticker+" = "+balanceUrl)
                if config.VERBOSE: print(jsonObj)

    return config.ALL_MEANS_ONCE

### ###########################################################
# Fetch and print balances from any exchange based on bitshares.
def balances_bit_shares(source, scopeTickers):        
    printSource = source+"\n  "

    proc = subprocess.Popen(['/opt/mining/mining/balances/bit-shares.py', source], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
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
        ticker = val_coin[1].replace('BRIDGE.','')
        if not scopeTickers or ticker in scopeTickers:
            #print('  '+ticker + " " + value)
            printBalance(printSource, ticker, float(value.replace(',','')))
            printSource = '  '

### ###############################################################################
def getUrlToJsonObj(config, balanceUrl, source, ticker='all'):
    jsonStr = getUrlToStr(config, balanceUrl, source, ticker, 'json')
    return json.loads(jsonStr)

### ###############################################################################
def getUrlToStr(config, balanceUrl, source='source', ticker='ticker', encoding='html'):
    proc = subprocess.Popen(['curl', '--insecure', '--compressed', balanceUrl], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    curlStr, err = proc.communicate(None)
    curlStr = curlStr.decode()
    if err:
        if config.VERBOSE: print(err, file=sys.stderr)
    if config.PRINT:
        printFilename = '/tmp/' + source.lower()
        if ticker != 'all':
            printFilename += '-' + ticker.lower()
        printFilename += '-balances.' + encoding
        with open(printFilename, 'w') as f: f.write(curlStr)
        print("Data downloaded from : " + balanceUrl + "\n            saved in " + printFilename)
    return curlStr

### ###########################################################
### Print coin's name and balance. 'tabber' might hold the
###   source's 'name<LF>  ' or just '  '. printBalance() also
###   accumulates the total balance per ticker.
def printBalance(tabber, ticker, balance):
    global TOTALS, Config
    if ticker not in TOTALS: TOTALS[ticker] = 0
    TOTALS[ticker] += balance
    if not Config.QUICK:
        print("%s%s %0.8f"%(tabber, ticker, balance))
    
    
### ###########################################################
def load_config():
    with open("/opt/mining/conf/sources.yml", 'r') as stream:
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
        print(' '.join(source.lower() for source in SOURCES_YML['SOURCES'])+' --scope')

def initialize(self, config, coin):
    load_config()
    config.DRYRUN = True # we're just experimenting for the time being; lot's of testing to be done!
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    global TOTALS

    if not config.QUICK:
        print("\n")
    printSource = "**TOTALS**\n  "
    for ticker in sorted(TOTALS):
        if TOTALS[ticker]:
            if TOTALS[ticker] < 10:
                print("%s%s %0.8f"%(printSource, ticker, TOTALS[ticker]))
            elif TOTALS[ticker] < 100:
                print("%s%s %.4f"%(printSource, ticker, TOTALS[ticker]))
            elif TOTALS[ticker] < 1000:
                print("%s%s %0.3f"%(printSource, ticker, TOTALS[ticker]))
            elif TOTALS[ticker] < 10000:
                print("%s%s %0.2f"%(printSource, ticker, TOTALS[ticker]))
            elif TOTALS[ticker] < 100000:
                print("%s%s %0.1f"%(printSource, ticker, TOTALS[ticker]))
            else:
                print("%s%s %0.0f"%(printSource, ticker, TOTALS[ticker]))
            printSource = '  '

    return config.ALL_MEANS_ONCE
