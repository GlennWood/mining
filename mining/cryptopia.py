from __future__ import print_function
import subprocess
import sys
import cryptopia_api

'''

Ref: https://www.cryptopia.co.nz/Forum/Thread/255 (the API doc)

curl 'https://www.cryptopia.co.nz/api/GetMarket/100/&market=ETH_GBX'
{"Success":true,"Message":null,"Data":{
  "TradePairId":100,
  "Label":"DOT/BTC",
  "AskPrice":0.00000398,
  "BidPrice":0.00000393,
  "Low": 0.00000326,
  "High":0.00000429,
  "Volume":10423979.43255571,
  "LastPrice":0.00000397,
  "BuyVolume":74342900.01457408,
  "SellVolume":27488137.46032763,
  "Change":15.41,
  "Open": 0.00000344,
  "Close":0.00000397,
  "BaseVolume":40.98709556,
  "BuyBaseVolume":63.34914530,
  "SellBaseVolume":512227661.89152766},
  "Error":null
}

curl 'https://www.cryptopia.co.nz/api/GetMarket/100/&market=GBX_ETH'    
{"Success":true,"Message":null,"Data":{
  "TradePairId":100,
  "Label":"DOT/BTC",
  "AskPrice":0.00000398,
  "BidPrice":0.00000393,
  "Low": 0.00000326,
  "High":0.00000429,
  "Volume":10423979.43255571,
  "LastPrice":0.00000397,
  "BuyVolume":74342900.01457408,
  "SellVolume":27515885.83108376,
  "Change":15.41,
  "Open": 0.00000344,
  "Close":0.00000397,
  "BaseVolume":40.98709556,
  "BuyBaseVolume":63.34914530,
  "SellBaseVolume":512227662.00226618
}'''

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['COIN']+")")

    cryptopia = cryptopia_api.Api(key='', secret='')
    
    balance, error = cryptopia.get_balance(coin['COIN'])
    if error is not None:
        print('ERROR: %s' % error, file=sys.stderr)
    else:
        print ('Request successful. Balance in ',coin['COIN'],' = %f' % balance)

def initialize(self, config, coin):
    COIN = coin['COIN'].upper()
    if config.VERBOSE: print(__name__+".initialize("+coin['COIN']+")")

    url = 'https://www.cryptopia.co.nz/api/GetMarket/100/&market=$COIN_ETH'.replace('$COIN', COIN)
    proc = subprocess.Popen(['curl', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    htmlStr, err = proc.communicate(None)
    if err: print(err, file=sys.stderr);return False

    if config.PRINT:
        printFilename = COIN + '-exchange.json'
        with open(printFilename, 'w') as f: f.write(htmlStr)
        print("Data downloaded from : " + url + "\n            saved in " + printFilename)
        
    print(COIN+" / ETH =")

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['COIN']+")")
    return 0
