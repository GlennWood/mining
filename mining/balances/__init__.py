from __future__ import print_function
### Ref: http://python-future.org/compatible_idioms.html
from builtins import range
import subprocess
import json
import sys
import os
import re
import yaml
from datetime import datetime
import locale

TOTALS = { }
ExchangeRates = { }
SOURCES_YML = None
COMMON_TO_SYMBOL = { }
SYMBOL_TO_COMMON = { }
BTC2USD = None

Config = None

### ###########################################################
def process(self, config, coin):
    global Config, COMMON_TO_SYMBOL

    SOURCES_YML = Config.load_sources_yml()
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
        try: # this is to capture KeyboardInterrupt and ImportError, allowing us to proceed with other sources
            importError = None
            srcs = sourceToDo.split(':')
            source = srcs[0].upper()
            if len(srcs) > 1:
                scopeTickers = srcs[1].upper().split(',')
            else:
                scopeTickers = None
            
            printSource = source+"\n  "
            if config.VERBOSE:
                print(printSource,end='')
                printSource = ''
    
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
                elif not balanceUrls:
                    balanceUrls = ['']
                    
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
                    print(printSource+ticker+" Cannot read key file for "+source+":"+ticker+", "+str(ex), file=sys.stderr)
                    continue
    
                balanceUrl = balanceUrls[0]
                if balanceUrl is None: balanceUrl = ''
                if config.VERBOSE and source not in OWN_READER and balanceUrl not in OWN_READER:
                    print('URL: '+balanceUrl)
            
                ### ####################################################### ###
                # Parse the downloaded data according to each pool's format.
                if balanceUrl.startswith('MPOS:'):# or source == 'AIKAPOOL' or source == 'SUPRNOVA':
                    try:
                        url = balanceUrl.split(':',1)[1]+'/index.php?page=api&action=getuserbalance&api_key=$API_KEY&id=$API_ID' \
                                    .replace('$API_ID', secrets_json['api_id']).replace('$API_KEY', secrets_json['api_key'])
                        jsonObj = getUrlToJsonObj(url, source, ticker)
                        data = jsonObj['getuserbalance']['data']
                        printBalance(printSource, ticker, float(data['confirmed'])+float(data['unconfirmed']))
                        printSource = '  '
                    except:
                        print(printSource+ticker+' ERROR: '+str(jsonObj))
                        printSource = '  '
        
                elif source == 'ALHAFEEZ':
                    print("  ALHAFEEZ is NYI")
                    print(balanceUrl)
                    htmlStr = getUrlToStr(balanceUrl)
                    print(htmlStr)
                    
                elif source == 'ANORAK':
                    jsonStr = getUrlToStr(balanceUrl, source, ticker, 'jsons')
                    if config.VERBOSE: print(jsonStr)
    
                ### Ref: https://github.com/binance-exchange/binance-official-api-docs
                elif source == 'BINANCE':
                    importError = "Perhaps module 'binance.client' is not installed: try 'sudo pip3 install python-binance'"
                    from binance.client import Client
                    #from binance.client import BinanceAPIException
                    client = Client(secrets_json['api_key'], secrets_json['api_secret'])
                    data = client.get_asset_balance(asset=ticker)
                    printBalance(printSource, data['asset'], float(data['free'])+float(data['locked']))
                    printSource = '  '

                elif source == 'BLEUTRADE':
                    from balances.bleutradeapi import Bleutrade
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
    
                elif source == 'COINBASE':
                    try:
                        from balances.coinbaseapi import Coinbase
                        accounts = Coinbase(secrets_json['api_key'], secrets_json['api_secret']).accounts()
                        for data in accounts['data']:
                            tckr = data['balance']['currency']
                            if scopeTickers and tckr != 'all' and tckr not in scopeTickers:
                                if config.VERBOSE: print("TICKER:"+tckr+" not in "+str(scopeTickers))
                            else:
                                printBalance(printSource, tckr, float(data['balance']['amount']))
                                printSource = '  '
                    except:
                        ex = sys.exc_info()[0]
                        print(printSource+str(ex), file=sys.stderr)
                        print(printSource+"Is module coinbase installed? Do 'sudo "+config.PIP+" install coinbase'",file=sys.stderr)
                
                elif balanceUrl == 'exx-api':
                    try:
                        from exx.client import Client
                        from exx.exceptions import ExxAPIException
                        client = Client(secrets_json['api_key'], secrets_json['api_secret'], user_agent='')
                        funds = client.get_balance()
                        for key, val in funds['funds'].items():
                            if val['balance'] != '0':
                                if not scopeTickers or val['propTag'] in scopeTickers:
                                    printBalance(printSource, val['propTag'], float(val['balance']))
                                    printSource = '  '
                    except ExxAPIException as ex:
                        print(ex)
                    except:
                        ex = sys.exc_info()[0]
                        print( "Unknown exception in EXX: "+str(ex), file=sys.stderr )
 
                elif balanceUrl == 'cryptopia-api':
                    try:
                        from balances.cryptopia_api import Api
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
                    except:
                        ex = sys.exc_info()[0]
                        print( "Unknown exception in balances.cryptopia_api: "+str(ex), file=sys.stderr )

                elif source == 'MININGPOOLHUB':
                    try:
                        jsonObj = getUrlToJsonObj(balanceUrl, source, ticker)
                        for coin in jsonObj['getuserallbalances']['data']:
                            tot = coin['confirmed'] + coin['unconfirmed']+ coin['ae_confirmed'] + coin['ae_unconfirmed'] + coin['exchange']
                            tckr = COMMON_TO_SYMBOL[coin['coin']]
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
                            jsonObj = getUrlToJsonObj(balanceUrl, source, ticker)
                            if 'error' in jsonObj['result']:
                                print('  BTC ERROR: %s'%(jsonObj['result']['error']))
                            else:
                                total = float(jsonObj['result']['balance_confirmed'])+float(jsonObj['result']['balance_pending'])
                                if len(balanceUrls) > 1:
                                    statsObj = getUrlToJsonObj(balanceUrls[1], source, ticker)
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
                    import gdax
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
    
                elif balanceUrl == 'bitshares-api':
                    #balances_bit_shares(config, secrets_json, source, scopeTickers)
                    from balances.bitsharesapi import BitSharesAccount
                    amounts = BitSharesAccount(secrets_json['account']).amounts
                    for key, value in amounts.items():
                        if not scopeTickers or key in scopeTickers:
                            printBalance(printSource, key, value)
                            printSource = '  '
    
                elif balanceUrl.startswith('yiimp:'): # aka UNIMINING, ZPOOL
                    # Ref: https://www.unimining.net/api
                    try:
                        url = balanceUrl.split(':',1)[1]+'/api/walletEx?address=$API_ID'.replace("$API_ID", secrets_json['api_id'])
                        jsonObj = getUrlToJsonObj(url, source, ticker)
                        printBalance(printSource, ticker, jsonObj['total'])
                        printSource = '  '
                    except json.decoder.JSONDecodeError as ex:
                        # unimining/api returned nothing; probably their throttling mechanism; let's read it from the WebUI
                        url = balanceUrl.split(':',1)[1]+'/site/wallet_results?address=$API_ID&showdetails=1'.replace("$API_ID", secrets_json['api_id'])
                        webHtml = getUrlToStr(url, source, ticker)
                        if ticker in SYMBOL_TO_COMMON:
                            tckr = SYMBOL_TO_COMMON[ticker]
                        else:
                            tckr = ticker
                        regex = re.compile('.*?Total Earned.*?([0-9]*[.][0-9]*) '+tckr+'.*')
                        match = regex.match(webHtml)
                        if match:
                            balance = match.group(1)
                            printBalance(printSource, ticker, float(balance))
                            printSource = '  '
    
                else:
                    if not balanceUrl: balanceUrl = '<None>'
                    print("Don't know how to process "+source+':'+ticker+" = "+balanceUrl)

        except KeyboardInterrupt as ex:
            print(printSource+'KeyboardInterrupt in '+source, file=sys.stderr)
        except ImportError as ex:
            print(printSource+str(ex))
            printSource = '  '
            if importError:
                print(printSource+importError)
        except Exception as ex:
            if config.VERBOSE: print(str(ex))
            print (printSource+ex.message)

    return config.ALL_MEANS_ONCE

### ###########################################################
# Fetch and print balances from any exchange based on bitshares.
# Ref: Ref: https://github.com/bitshares/python-bitshares/blob/master/docs/tutorials.rst

def balances_bit_shares(config, secrets_json, source, scopeTickers):
    printSource = '' # this is cleaner than passing printSource as a param.
    if not config.VERBOSE: printSource = source+"\n  " # VERBOSE already printed it.

    from bitshares import BitShares
    amounts = BitShares(config, secrets_json['account'])
    for key, value in amounts.items():
        if not scopeTickers or key in scopeTickers:
            printBalance(printSource, key, value)
            printSource = '  '

    try: # bitshares.account will work under Python3, but throw exception if Python2
        from bitshares.account import Account
        account = Account(secrets_json['account'])
        print (account.json())
        # We add the balances and open-orders amounts, since we still own unfilled open-orders
        amounts = { }
        for balance in account.balances:
            ticker = balance.symbol.replace('BRIDGE.','')
            if ticker not in amounts: amounts[ticker] = 0
            amounts[ticker] += balance.amount
        for openorder in account.openorders:
            order = openorder['base']
            ticker = order.symbol.replace('BRIDGE.','')
            if ticker not in amounts: amounts[ticker] = 0
            amounts[ticker] += order.amount
        for key, value in amounts.items():
            if not scopeTickers or key in scopeTickers:
                printBalance(printSource, key, value)
                printSource = '  '
        return ''
    except KeyboardInterrupt as ex:
        raise KeyboardInterrupt()
    except:
        ex = sys.exc_info()[0]
        if config.VERBOSE: print( "Exception in balances.balances_bit_shares(): "+str(ex), file=sys.stderr )

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

### ###########################################################
def getUrlToJsonObj(balanceUrl, source='source', ticker='all'):
    jsonStr = getUrlToStr(balanceUrl, source, ticker, encoding='json')
    return json.loads(jsonStr)

### ###############################################################################
def getUrlToStr(balanceUrl, source='source', ticker='ticker', encoding='html'):
    global Config

    cmd = ['curl', '--insecure', '--compressed', balanceUrl]
    if encoding == 'json': cmd.extend(['-H',  "accept: application/json"])

    proc = subprocess.Popen(['curl', '--insecure', '--compressed', balanceUrl], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    curlStr, err = proc.communicate(None)
    curlStr = curlStr.decode()
    if err:
        if Config.VERBOSE: print(err, file=sys.stderr)
    if Config.PRINT:
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

### ##############################################################
### Return value of 'val' 'ticker' coins in dollars.
def value_in_dollars(ticker, val):
    global ExchangeRates, BTC2USD, SYMBOL_TO_COMMON

    btc_rate = ExchangeRates['rates']
    if ticker.lower() in btc_rate:    
        btc_rate = btc_rate[ticker.lower()]['value']
        if btc_rate == 0: btc_rate = 1
        return (BTC2USD / btc_rate) * val

    if ticker not in SYMBOL_TO_COMMON:
        return 'NaN'

    tckr = SYMBOL_TO_COMMON[ticker]
    rate = getUrlToJsonObj('https://api.coingecko.com/api/v3/coins/'+tckr+'?localization=false')['market_data']['current_price']
    if 'usd' not in rate:
        print (rate['market_data']['current_price'])
        return 'NaN'
    return rate['usd'] * val

### ##############################################################
### Add SCOPING (from sources.yml) as options to 'miners balance'
def bash_completion(self,prev):
    with open("/opt/mining/conf/sources.yml", 'r') as stream:
        try:
            SOURCES_YML = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)
    if prev == '--scope':
        print(' '.join(scope.lower() for scope in SOURCES_YML['SCOPING']))
    else:
        print(' '.join(source.lower() for source in SOURCES_YML['SOURCES'])+' --scope')

### ###########################################################
def initialize(self, config, coin):
    global Config, SOURCES_YML, ExchangeRates, BTC2USD, COMMON_TO_SYMBOL, SYMBOL_TO_COMMON
    Config = config
    
    # Ref: https://www.coingecko.com/api/docs/v3#/coins/get_coins_list
    coingeckoSymbols = getUrlToJsonObj('https://api.coingecko.com/api/v3/coins/list')
    for symbol in coingeckoSymbols:
        COMMON_TO_SYMBOL[symbol['id']] = symbol['symbol'].upper()
        SYMBOL_TO_COMMON[symbol['symbol'].upper()] = symbol['id']

    # Ref: https://www.coingecko.com/api/docs/v3#/exchange_rates/get_exchange_rates
    ExchangeRates = getUrlToJsonObj("https://api.coingecko.com/api/v3/exchange_rates")
    BTC2USD = ExchangeRates['rates']['usd']['value']
    return config.ALL_MEANS_ONCE

### ###########################################################
def finalize(self, config, coin):
    global TOTALS, ExchangeRates

    if not config.QUICK:
        print("\n")
    printSource = "**TOTALS**\n  "
    total_usd = 0
    for ticker in sorted(TOTALS):
        if TOTALS[ticker]:
            usd = value_in_dollars(ticker, TOTALS[ticker])
            if usd == 'NaN':
                usd = ''
            else:
                total_usd += usd
                usd = " $%0.2f"%(usd)

            if TOTALS[ticker] < 10:
                print("%s%s %0.8f%s"%(printSource, ticker, TOTALS[ticker], usd))
            elif TOTALS[ticker] < 100:
                print("%s%s %.4f%s"%(printSource, ticker, TOTALS[ticker], usd))
            elif TOTALS[ticker] < 1000:
                print("%s%s %0.3f%s"%(printSource, ticker, TOTALS[ticker], usd))
            elif TOTALS[ticker] < 10000:
                print("%s%s %0.2f%s"%(printSource, ticker, TOTALS[ticker], usd))
            elif TOTALS[ticker] < 100000:
                print("%s%s %0.1f%s"%(printSource, ticker, TOTALS[ticker], usd))
            else:
                print("%s%s %0.0f%s"%(printSource, ticker, TOTALS[ticker], usd))
            printSource = '  '

    timestamp = datetime.now()
    time_format = locale.nl_langinfo(locale.D_T_FMT)
    print("\n**TOTAL USD**  $%0.2f  - %s"%(total_usd, timestamp.strftime(time_format)))

    return config.ALL_MEANS_ONCE
