from __future__ import print_function
import subprocess
import json
import time
import sys

### Ref: https://github.com/miningpoolhub/php-mpos/wiki/API-Reference
###   https://[<coin_name>.]miningpoolhub.com/index.php?page=api&action=<method>&api_key=<user_api_key>[&<argument>=<value>]

### Ref: https://www.unimining.net/api/currencies

### MiningPoolStats - alternative to other MPH api's
###    https://miningpoolhubstats.com/USD/$MININGPOOLHUB_APIKEY

BalanceUrls = [
'cryptopia',
'https://miningpoolhub.com/index.php?page=api&action=getuserallbalances&api_key=d874359501d77ee4fabdb57d50c33f89c031018bc3262bb962f8c9294727f9cb',
'https://www.unimining.net/api/walletEx?address=GQfzRW76zJX9DKg3mbmqqZpxRNh25TUUSo',
'https://www.unimining.net/api/walletEx?address=TbsMq8Woobty7dbyYFQFDrDZiPja52QDQc'
]

COMMON_TO_SYMBOL = {
  'ethereum': 'ETH',
  'expanse': 'EXP',
  'zcash': 'ZEC',
  'musicoin': 'MUSIC',
  'zencash': 'ZEN'
}


def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['Coin']+")")

    UNIMINING_THROTTLE=False

    for balanceUrl in BalanceUrls:
        RETRYING_IS_OK=True
        while RETRYING_IS_OK:
            RETRYING_IS_OK=False

        if 'unimining' in balanceUrl and UNIMINING_THROTTLE:
            for t in xrange(0,65):
                print('\rPausing to accommodate unimining\'s throttling...'+str(65-t)+' ',end=''),;sys.stdout.flush()
                time.sleep(1)
                print ('\r'),;sys.stdout.flush()
        UNIMINING_THROTTLE=False
        
        #balanceUrl = statsUrl.replace('$WALLET', str(coin['Wallet'])).replace('$COIN', coin['Coin'].lower())
        if config.VERBOSE: print('curl '+balanceUrl)
        proc = subprocess.Popen(['curl', balanceUrl], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        jsonStr, err = proc.communicate(None)
        #if err: print(err, sep=' ', end='\n', file=sys.stderr)
        
        if config.PRINT:
            encoding = 'html'
            if 'isJson' in balanceUrl: encoding = 'json'
            printFilename = 'balances.' + encoding
            with open(printFilename, 'w') as f: f.write(jsonStr)
            print("Data downloaded from : " + balanceUrl + "\n            saved in " + printFilename)
    
        # Parse the downloaded data according to each pool's format
        if 'miningpoolhub' in balanceUrl:
    
            balances = json.loads(jsonStr)
            for coin in balances['getuserallbalances']['data']:
                print(COMMON_TO_SYMBOL[coin['coin']]+': ='+str(coin['confirmed'])+'+'+str(coin['unconfirmed'])+ '+'+str(coin['ae_unconfirmed']))
    
        elif 'unimining' in balanceUrl:
            UNIMINING_THROTTLE=True
  
            # Ref: https://www.unimining.net/api
            if jsonStr == '':
                print('???'+': Unimining/api returned nothing; probably their throttling mechanism; retrying now.')
                RETRYING_IS_OK=True
            else:
  
                balances = json.loads(jsonStr)
      
                unsold  = balances['unsold']
                balance = balances['balance']
                unpaid  = balances['unpaid']
                #paid24h = balances['paid24h']
                total   = balances['total']
                  
                print(balances['currency']+': total ='+str(total)+' pending ='+str(unsold)+' unpaid ='+str(unpaid)+' balance ='+str(balance))
  
        elif 'cryptopia' in balanceUrl:
            print("balance/cryptopia is NYI")
            
        else:
            print("Don't know how to process balanceUrl="+balanceUrl)
  
    return None

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['Coin']+")")

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['Coin']+")")
    return 0
