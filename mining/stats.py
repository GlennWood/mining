import config
import os
import subprocess
import re
import json

### Ref: https://github.com/miningpoolhub/php-mpos/wiki/API-Reference
###   https://[<coin_name>.]miningpoolhub.com/index.php?page=api&action=<method>&api_key=<user_api_key>[&<argument>=<value>]

def process(self, config, coin):
    StatsUrls = config.StatsUrls
    print StatsUrls
    
    if coin['Coin'] is None or not coin['Coin'] in StatsUrls:
      print coin['Coin'] + ': ' + ' StatsUrl has not been configured for '+coin['Coin']+'; see '+config.MINERS_XLSX
      return 1

    coinUrls = StatsUrls[coin['Coin']]
    if VERBOSE: print coinUrls
    if coinUrls: 
      statsParser = coinUrls[0]
      statsUrl = coinUrls[1]
    if statsUrl is None:
      if statsParser == 'unimining':
          statsUrl = 'https://www.unimining.net/site/wallet_results?address=$WALLET&showdetails=0'
      elif statsParser == 'cryptopools':
          statsUrl = 'http://pirl.cryptopools.info/api/accounts/$WALLET'
      else:
          print 'A statsUrl for '+coin_+' has not been configured'
          return 1

    if config.VERBOSE: print 'StatsUrl: '+str(statsUrl)
    coin_ = coin['Coin']
    statsUrl = statsUrl.replace('$WALLET', str(coin['Wallet'])).replace('$COIN', coin['Coin'].lower())
    proc = subprocess.Popen(['curl', statsUrl], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    htmlStr, err = proc.communicate(None)
    if config.PRINT:
      encoding = 'html'
      if statsParser == 'cryptopools': encoding = 'json'
      printFilename = coin['Coin'] + '-' + statsParser + '.' + encoding
      with open(printFilename, 'w') as f: f.write(htmlStr)
      print "Data downloaded from : " + statsUrl + "\n            saved in " + printFilename

    # Parse the downloaded data according to each pool's format
    if statsParser == 'cryptopools':

        stats = json.loads(htmlStr)
        print "Current hashrate: " + '%.2f'%(float(stats['currentHashrate'])/1000000) + ' Mh/s'
        print "Longterm hashrate: " + '%.2f'%(float(stats['hashrate'])/1000000) + ' Mh/s'
        print "Immature: " + str(float(stats['stats']['immature'])/1000000000)
        print "Pending: " + str(float(stats['stats']['pending'])/1000000000)
        print "Balance: " + str(float(stats['stats']['balance'])/1000000000)
        print "Paid " + coin['Coin'] + ": " + str(float(stats['stats']['paid'])/1000000000)

    elif statsParser == 'unimining':
        ### This is for https://www.unimining.net/site/wallet_results?address=$WALLET
        regex = re.compile(r'.*?<td .*?Total Unpaid</b></td><td [^<]*</td><td [^>]*>(<a href=[^>]*>)?([0-9]*[.][0-9]*).*', re.DOTALL)
        match = regex.match(htmlStr)
        val = match.group(2)
        print coin['Coin'] + ': ' + val + ': Unpaid'
        regex = re.compile(r'.*?<td .*?Total Paid</b></td><td [^<]*</td><td [^>]*>(<a href=[^>]*>)?([0-9]*[.][0-9]*).*', re.DOTALL)
        match = regex.match(htmlStr)
        val = match.group(2)
        print coin['Coin'] + ': ' + val + ': Paid'
        regex = re.compile(r'.*?<td .*?Total Earned</b></td><td [^<]*</td><td [^>]*>(<a href=[^>]*>)?([0-9]*[.][0-9]*).*', re.DOTALL)
        match = regex.match(htmlStr)
        val = match.group(2)
        print coin['Coin'] + ': ' + val+ ': Earned'

    return None

def finalize(self, config, coin):
	return 0
