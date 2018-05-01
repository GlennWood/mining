import subprocess
import json
import time
import sys
from cryptopia_api import Api

### Ref: https://github.com/miningpoolhub/php-mpos/wiki/API-Reference
###   https://[<coin_name>.]miningpoolhub.com/index.php?page=api&action=<method>&api_key=<user_api_key>[&<argument>=<value>]

### Ref: https://www.unimining.net/api/currencies

### MiningPoolStats - alternative to other MPH api's
###    https://miningpoolhubstats.com/USD/$MININGPOOLHUB_APIKEY

BalanceUrls = [
'https://miningpoolhub.com/index.php?page=api&action=getuserallbalances&api_key=$API_KEY',
'https://www.unimining.net/api/walletEx?address=GQfzRW76zJX9DKg3mbmqqZpxRNh25TUUSo',
'https://www.unimining.net/api/walletEx?address=TbsMq8Woobty7dbyYFQFDrDZiPja52QDQc',
'https://kmd.suprnova.cc/index.php?page=api&action=getuserbalance&api_key=07909084c493f7761b05556286c5f242e71eb9a266ba00e2127a26f5496b7db7&id=201810265',
'cryptopia',
'crypto-bridge'
]

COMMON_TO_SYMBOL = {
  'bitcoin-private': 'BTCP',
  'bitcoin-gold': 'BTG',
  'ethereum': 'ETH',
  'expanse': 'EXP',
  'zcash': 'ZEC',
  'musicoin': 'MUSIC',
  'zclassic': 'ZCL',
  'zencash': 'ZEN'
}


def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['COIN']+")")

    UNIMINING_THROTTLE=False

    for balanceUrl in BalanceUrls:
        RETRYING_IS_OK=True
        while RETRYING_IS_OK:
            RETRYING_IS_OK=False

        if 'unimining' in balanceUrl and UNIMINING_THROTTLE:
            for t in xrange(0,65):
                print('\rPausing to accommodate unimining\'s throttling (use "-q" to bypass this)...'+str(65-t)+' '),;sys.stdout.flush()
                time.sleep(1)
                print ('\r'),;sys.stdout.flush()
        UNIMINING_THROTTLE=False
        
        if 'miningpoolhub' in balanceUrl:
            with open('/etc/mining/miningpoolhub.key') as secrets:
                secrets_json = json.load(secrets)
                secrets.close()
            balanceUrl = balanceUrl.replace('$API_KEY',secrets_json['key'])

        #balanceUrl = statsUrl.replace('$WALLET', str(coin['Wallet'])).replace('$COIN', coin['COIN'].lower())
        if config.VERBOSE: print('curl '+balanceUrl)
        proc = subprocess.Popen(['curl', balanceUrl], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        jsonStr, err = proc.communicate(None)
        #if err: print(err, sep=' ', end='\n', file=sys.stderr)
        if err:
            if config.VERBOSE: print err
            next

        if config.PRINT:
            encoding = 'html'
            if 'isJson' in balanceUrl or 'miningpoolhub' in balanceUrl: encoding = 'json'
            printFilename = 'balances.' + encoding
            with open(printFilename, 'w') as f: f.write(jsonStr)
            print("Data downloaded from : " + balanceUrl + "\n            saved in " + printFilename)
    
        # Parse the downloaded data according to each pool's format
        if 'miningpoolhub' in balanceUrl:
            with open('/etc/mining/miningpoolhub.key') as secrets:
                secrets_json = json.load(secrets)
                secrets.close()
            balanceUrl = balanceUrl.replace('$API_KEY',secrets_json['key'])

            balances = json.loads(jsonStr)
            for coin in balances['getuserallbalances']['data']:
                print(COMMON_TO_SYMBOL[coin['coin']]+' '+str(coin['confirmed'])+'+'+str(coin['unconfirmed'])+ '+'+str(coin['ae_unconfirmed']))
    
        elif 'unimining' in balanceUrl:
            #UNIMINING_THROTTLE=True
  
            # Ref: https://www.unimining.net/api
            if jsonStr == '':
                if config.QUICK:
                    print('???'+' unimining/api returned nothing; probably their throttling mechanism; quickly bypassing that balance.')
                    UNIMINING_THROTTLE=False
                else:
                    print('???'+' unimining/api returned nothing; probably their throttling mechanism; retrying now.')
                    RETRYING_IS_OK=True
            else:
                if not config.QUICK:
                    UNIMINING_THROTTLE=True

                balances = json.loads(jsonStr)
      
                #unsold  = balances['unsold']
                #balance = balances['balance']
                #unpaid  = balances['unpaid']
                #paid24h = balances['paid24h']
                total   = balances['total']
                  
                #print(balances['currency']+' total ='+str(total)+' pending ='+str(unsold)+' unpaid ='+str(unpaid)+' balance ='+str(balance))
                print(balances['currency']+' '+str(total))
  
        elif 'cryptopia' in balanceUrl:
            #print("balance/cryptopia is NYI")
            api_wrapper = Api('/etc/mining/cryptopia.key',None)
            
            #call a request to the api, like balance in BTC...
            balance, error = api_wrapper.get_balance('ZCL')
            if error is not None:
                print 'ERROR: %s' % error
            else:
                #print balance
                ## "{u'Available': 0.275625, u'Status': u'OK', u'PendingWithdraw': 0.0, u'CurrencyId': 395,
                ##   u'Symbol': u'ZCL', u'HeldForTrades': 0.0, u'Address': None, 
                ##   u'BaseAddress': None, u'Total': 0.275625, u'StatusMessage': None, u'Unconfirmed': 0.0}"
                print balance['Symbol'] + " " + str(balance['Total'])

        elif 'crypto-bridge' in balanceUrl:
            proc = subprocess.Popen(['/usr/bin/python3','/opt/mining/mining/crypto-bridge.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            out, err = proc.communicate(None)
            if err:
                if config.VERBOSE: print err
            else:
                lines = out.splitlines()
                # "[0.00001017 BRIDGE.BTC, 162.1362 BRIDGE.RVN]"
                line = lines[0].replace('[','').replace(']','')
                vals = line.split(", ")
                for val in vals:
                    val_coin = val.split(' ')
                    value = val_coin[0]
                    coin = val_coin[1].replace('BRIDGE.','')
                    print coin + " " + value

        elif 'suprnova' in balanceUrl:
            balances = json.loads(jsonStr)
            coin = balanceUrl.replace('https://','').split('.')[0].upper()
            ''' 
            {u'confirmed': 0.53601572, u'orphaned': 0, u'unconfirmed': 0.03763759}
            print balances{'getuserbalance'}{''}
            '''
            data = balances['getuserbalance']['data']
            print coin + ' ' + str(data['confirmed'])+'+'+str(data['unconfirmed'])
            #for coin in balances['getuserallbalance']['data']:
            #    print(COMMON_TO_SYMBOL[coin['coin']]+': ='+str(coin['confirmed'])+'+'+str(coin['unconfirmed'])+ '+'+str(coin['ae_unconfirmed']))

        else:
            print("Don't know how to process balanceUrl="+balanceUrl)
  
    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['COIN']+")")
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['COIN']+")")
    return config.ALL_MEANS_ONCE
