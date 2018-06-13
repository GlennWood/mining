from __future__ import print_function
### Ref: http://python-future.org/compatible_idioms.html
from builtins import range
import subprocess
import json
import time
import sys
import os
from balances.cryptopia_api import Api
import gdax

### Ref: https://github.com/miningpoolhub/php-mpos/wiki/API-Reference
###   https://[<coin_name>.]miningpoolhub.com/index.php?page=api&action=<method>&api_key=<user_api_key>[&<argument>=<value>]

### Ref: https://www.unimining.net/api/currencies

### MiningPoolStats - alternative to other MPH api's
###    https://miningpoolhubstats.com/USD/$MININGPOOLHUB_APIKEY
### Ref: https://github.com/miningpoolhub/php-mpos/wiki/API-Reference

### Ref: 
###      https://api.nicehash.com/api?method=balance&id=$API_ID&key=4API_KEY

SOURCES = {
'GDAX': {'all': 'sandbox'},
'NICEHASH': { 'all': 'https://api.nicehash.com/api?method=balance&id=$API_ID&key=$API_KEY' },
'MININGPOOLHUB': { 'all': 'https://miningpoolhub.com/index.php?page=api&action=getuserallbalances&api_key=$API_KEY' },
'UNIMINING': {
    'GBX': 'https://www.unimining.net/api/walletEx?address=GQfzRW76zJX9DKg3mbmqqZpxRNh25TUUSo',
    'TZC': 'https://www.unimining.net/api/walletEx?address=TbsMq8Woobty7dbyYFQFDrDZiPja52QDQc',
},
'SUPRNOVA': {
    'KMD': 'https://kmd.suprnova.cc/index.php?page=api&action=getuserbalance&api_key=07909084c493f7761b05556286c5f242e71eb9a266ba00e2127a26f5496b7db7&id=201810265',
},
'CRYPTOPIA': {'all': 'cryptopia'},
'CRYPTO-BRIDGE': {'all': 'bit-shares'},
'OPEN-LEDGER': {'all': 'bit-shares'},
}

COMMON_TO_SYMBOL = {
  'bitcoin-private': 'BTCP',
  'ethereum-classic': 'ETC',
  'bitcoin-gold': 'BTG',
  'ethereum': 'ETH',
  'expanse': 'EXP',
  'monero': 'XMR',
  'zcash': 'ZEC',
  'musicoin': 'MUSIC',
  'zclassic': 'ZCL',
  'zencash': 'ZEN'
}


def process(self, config, coin):

    if config.ALL_COINS: # meaning there was no command-line parameter following the OP 'balances_imp'
        Sources = sorted(SOURCES.keys())
    else:
        Sources = [ source.upper() for source in config.arguments['COIN'] ]

    miners_user_ssh = '/home/'+os.getenv('MINERS_USER')+'/.ssh/'
    UNIMINING_THROTTLE=False

    for source in Sources:
        if not source in SOURCES:
            print("'"+source+"' is an unknown source, expecting one of "+','.join(sorted(SOURCES.keys())),file=sys.stderr)
            continue
        print(source)
        RETRYING_IS_OK = True
        KEYBOARD_INTERRUPT = False

        while RETRYING_IS_OK and not KEYBOARD_INTERRUPT:
            RETRYING_IS_OK = False
            for ticker in SOURCES[source]:
                if KEYBOARD_INTERRUPT:
                    next

                if source == 'UNIMINING' and UNIMINING_THROTTLE:
                    try:
                        for t in range(0,65):
                            print('\rPausing to accommodate unimining\'s throttling (use "-q" to bypass this)...'+str(65-t)+' ',end='',file=sys.stderr),;sys.stderr.flush()
                            time.sleep(1)
                    except KeyboardInterrupt:
                        if config.VERBOSE: print('KeyboardInterrupt: miners balances_imp '+' '.join(config.arguments['COIN']))
                        KEYBOARD_INTERRUPT = True
                        RETRYING_IS_OK = False
                    print ('\r                                                                                 \r',end='',file=sys.stderr),;sys.stderr.flush()
                    if KEYBOARD_INTERRUPT:
                        print('  '+ticker+' KeyboardInterrupt')
                        next
                UNIMINING_THROTTLE=False
            
                balanceUrl = SOURCES[source][ticker]
                keyFile = miners_user_ssh + source.lower()
                if ticker != 'all':
                    keyFile += '-' + ticker.lower()
                secrets_json = None
                try:
                    with open(keyFile+'.key') as secrets:
                        secrets_json = json.load(secrets)
                        secrets.close()
                        if 'account' in secrets_json: balanceUrl = balanceUrl.replace('$ACCOUNT',secrets_json['account'])
                        if 'api_id'  in secrets_json: balanceUrl = balanceUrl.replace('$API_ID',secrets_json['api_id'])
                        if 'api_key' in secrets_json: balanceUrl = balanceUrl.replace('$API_KEY',secrets_json['api_key'])
                except IOError as ex:
                    print("  "+ticker+" Cannot read key file for "+source+", "+str(ex), file=sys.stderr)
                    next
                if config.VERBOSE and balanceUrl != 'bit-shares':  print ('URL: '+balanceUrl)

                jsonStr = '<NaS>'
                if balanceUrl and balanceUrl != 'bitshares':
                    proc = subprocess.Popen(['curl', balanceUrl], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    jsonStr, err = proc.communicate(None)
                    jsonStr = jsonStr.decode()
                    #if err: print(err, sep=' ', end='\n', file=sys.stderr)
                    if err:
                        if config.VERBOSE: print(err, file=sys.stderr)
                        next
        
                    if config.PRINT:
                        encoding = 'html'
                        if 'isJson' in balanceUrl or 'miningpoolhub' in balanceUrl: encoding = 'json'
                        printFilename = miners_user_ssh + source.lower()
                        if ticker != 'all':
                            printFilename += '-' + ticker.lower()
                        printFilename += '-balances_imp.' + encoding
                        with open(printFilename, 'w') as f: f.write(jsonStr)
                        print("Data downloaded from : " + balanceUrl + "\n            saved in " + printFilename)
            
                # Parse the downloaded data according to each pool's format
                if source == 'NICEHASH':
                    balances = json.loads(jsonStr)
                    if 'error' in balances['result']:
                        print("  ERROR: "+balances['result']['error'])
                    else:
                        print('  BTC'+' '+balances['result']['balance_confirmed'])
            
                elif source == 'MININGPOOLHUB':
                    try:
                        balances = json.loads(jsonStr)
                        for coin in balances['getuserallbalances']['data']:
                            tot = coin['confirmed'] + coin['unconfirmed']+ coin['ae_confirmed'] + coin['ae_unconfirmed'] + coin['exchange']
                            print('  '+COMMON_TO_SYMBOL[coin['coin']]+' '+str(tot))            
                    except:
                        print("  ERROR: "+jsonStr)
          
                elif source == 'CRYPTOPIA':
                    api_wrapper = Api(keyFile+'.key', None)
                    
                    balances, error = api_wrapper.get_balances()
                    if error is not None:
                        print('ERROR: %s' % error, file=sys.stderr)
                    else:
                        for balance in balances:
                            if balance['Total']:
                                print('  '+balance['Symbol'] + " " + str(balance['Total']))
        
                elif source == 'GDAX':
                    auth_client = gdax.AuthenticatedClient(secrets_json['api_key'], secrets_json['api_secret'], secrets_json['api_passphrase'])
                    accounts = auth_client.get_accounts()
                    for account in accounts:
                        balance = float(account['balance'])
                        
                        print("  "+account['currency']+" "+str(balance))
                elif source == 'SUPRNOVA':
                    try:
                        balances = json.loads(jsonStr)
                        coin = balanceUrl.replace('https://','').split('.')[0].upper()
                        ''' 
                        {u'confirmed': 0.53601572, u'orphaned': 0, u'unconfirmed': 0.03763759}
                        print balances_imp{'getuserbalance'}{''}
                        '''
                        data = balances['getuserbalance']['data']
                        print('  '+coin + ' ' + str(data['confirmed']+data['unconfirmed']))
                        #for coin in balances_imp['getuserallbalance']['data']:
                        #    print(COMMON_TO_SYMBOL[coin['coin']]+': ='+str(coin['confirmed'])+'+'+str(coin['unconfirmed'])+ '+'+str(coin['ae_unconfirmed']))
                    except:
                        print("  ERROR: "+jsonStr)
        
                elif source == 'UNIMINING':          
                    # Ref: https://www.unimining.net/api
                    if jsonStr == '':
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
            
                            balances = json.loads(jsonStr)
                            #unsold  = balances_imp['unsold']
                            #print(balances_imp['currency']+' total ='+str(total)+' pending ='+str(unsold)+' unpaid ='+str(unpaid)+' balance ='+str(balance))
                            print('  '+balances['currency']+' '+str(balances['total']))
                        except:
                            print("  ERROR: "+jsonStr)

                elif balanceUrl == 'bit-shares':


                    with open(miners_user_ssh + source.lower()+'.key') as secrets:
                        secrets_json = json.load(secrets)
                        secrets.close()
                    try:
                        eval('from bitshares.account import Account')
                        account = eval("Account("+secrets_json['account']+")")
                        out = "%s"%(account.balances)
                        print(out)
                        err = None
                    except:
                        proc = subprocess.Popen(['/usr/bin/python3','/opt/mining/mining/balances/bit-shares.py', source], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                        out, err = proc.communicate(None)
                    if err:
                        if config.VERBOSE: print(err,file=sys.stderr)
                    else:
                        lines = out.splitlines()
                        # "[0.00001017 BRIDGE.BTC, 162.1362 BRIDGE.RVN]"
                        line = lines[0].decode('utf-8').replace('[','').replace(']','')
                        vals = line.split(", ")
                        for val in vals:
                            val_coin = val.split(' ')
                            value = val_coin[0]
                            coin = val_coin[1].replace('BRIDGE.','')
                            print('  '+coin + " " + value)
            
                else:
                    print("Don't know how to process "+source+'-'+ticker+" = "+balanceUrl)
                    if config.VERBOSE: print(jsonStr)


    return config.ALL_MEANS_ONCE

def bash_completion():
    print(' '.join(source.lower() for source in SOURCES))

def initialize(self, config, coin):
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    return config.ALL_MEANS_ONCE
