from __future__ import print_function
from lxml import html
import sys
import os
import requests
import subprocess
### Ref: http://python-future.org/compatible_idioms.html
from builtins import range

NicehashToTicker = {
    'Nicehash-CNV7':'NH-CN',
    'Nicehash-Lyra2REv2':'NH-LY',
    'Nicehash-NeoScrypt':'NH-NS',
    'Nicehash-Equihash':'NH-EQ',
    'Nicehash-Ethash':'NH-ET',
    'Nicehash-Skunkhash': 'NH-SK',
    'Nicehash-NIST5': 'NH-NI',
    'Nicehash-CryptoNight': 'NH-CR'
}

def process(self, config, coin):
    global NicehashToTicker

    hostname = os.getenv('HOSTNAME')
    if not hostname: # So, HOSTNAME was not exported
        with open('/etc/hostname', 'r') as f: hostname = f.read().strip().upper()

    if config.SCOPE:
        return process_scope(self,config, coin)

    url = None
    for key in config.SHEETS['WhatToMine']:
        if hostname.find(key.upper()) >= 0:
            url = self.generateUrl(config, hostname, config.SHEETS['WhatToMine'][key])
            break
    if not url:
        print("Cannot match this hostname='"+hostname+"' with any key in miners.xslx/WhatToMine spreadsheet.", file=sys.stderr)
        return 1
    
    response = requests.get(url)
    response.raise_for_status()
    tree = html.fromstring(response.content)
    wtmList = tree.xpath("/html/body/div[@class='container']/table[@class='table table-hover table-vcenter']/tbody/tr")
    cnt = 0
    prev_revenue = prev_profit = None
    for tr in wtmList:
        cnt += 1
        coinName = tr.xpath("td[1]/div[2]/text()")
        if coinName and coinName[0].strip().startswith('Nicehash-'):
            coinName = coinName[0].strip()
            if coinName in NicehashToTicker:
                ticker = NicehashToTicker[coinName]
            else:
                print("Unrecognized Nicehash code: '"+coinName+"'", file=sys.stderr)
                continue
        else:
            coinName = tr.xpath("td[1]/div[2]/a/text()")
            if len(coinName) is 0:
                continue
            coinName, ticker = coinName[0].split('(')
            ticker = ticker.replace(')','')
        revenue_profit = tr.xpath("td[8]")
        
        revenue = revenue_profit[0].xpath("text()")
        profit = revenue_profit[0].xpath("strong/text()")
        if profit[0].find('-') < 0: # Let's skip the ones with negative profit.
            revenue = revenue[0].replace('$','').strip()
            profit  = profit[0].replace('$','').strip()
            if prev_revenue is None:
                prev_revenue = float(revenue)
                prev_profit  = float(profit)
            print(ticker + "," + revenue + "," + profit +
                  ','+str(int(((float(revenue)-prev_revenue) * 100 )/prev_revenue))+"%"+
                  ','+str(int(((float(profit)-prev_profit)  * 100 )/prev_profit))+"%"
                )
            prev_revenue = float(revenue)
            prev_profit  = float(profit)

        if cnt >= 7 and not config.VERBOSE:
            break

    return config.ALL_MEANS_ONCE

'''
Generate the WhatToMine url from the URL parameter, else by generating it from the param declaration rows.
'''
def generateUrl(config, hostname, column):
    if column['URL']:
        if config.VERBOSE: print("WhatToMine URL picked by 'url' parameter for hostname='"+hostname+"'", file=sys.stderr)
        return column['URL']
    print("WhatToMine URL generation is NYI", file=sys.stderr)    
    url = "https://whattomine.com/coins?utf8=%E2%9C%93&adapt_q_280x=0&adapt_q_380=0&adapt_q_fury=0&adapt_q_470=0&adapt_q_480=3&adapt_q_570=0&adapt_q_580=0&adapt_q_vega56=0&adapt_q_vega64=0&adapt_q_750Ti=0&adapt_q_1050Ti=0&adapt_q_10606=0&adapt_q_1070=6&adapt_1070=true&adapt_q_1070Ti=2&adapt_1070Ti=true&adapt_q_1080=0&adapt_q_1080Ti=0&adapt_1080Ti=true&eth=true&factor%5Beth_hr%5D=241.0&factor%5Beth_p%5D=990.0&grof=true&factor%5Bgro_hr%5D=274.0&factor%5Bgro_p%5D=1020.0&factor%5Bphi_hr%5D=158.0&factor%5Bphi_p%5D=1040.0&cn=true&factor%5Bcn_hr%5D=5040.0&factor%5Bcn_p%5D=780.0&cn7=true&factor%5Bcn7_hr%5D=5040.0&factor%5Bcn7_p%5D=780.0&eq=true&factor%5Beq_hr%5D=3520.0&factor%5Beq_p%5D=960.0&lre=true&factor%5Blrev2_hr%5D=295000.0&factor%5Blrev2_p%5D=1020.0&ns=true&factor%5Bns_hr%5D=8100.0&factor%5Bns_p%5D=1020.0&tt10=true&factor%5Btt10_hr%5D=150.0&factor%5Btt10_p%5D=960.0&x16r=true&factor%5Bx16r_hr%5D=68.0&factor%5Bx16r_p%5D=1030.0&skh=true&factor%5Bskh_hr%5D=228.0&factor%5Bskh_p%5D=960.0&n5=true&factor%5Bn5_hr%5D=364.0&factor%5Bn5_p%5D=1020.0&xn=true&factor%5Bxn_hr%5D=25.2&factor%5Bxn_p%5D=960.0&factor%5Bcost%5D=0.1&sort=Profitability24&volume=0&revenue=24h&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=binance&factor%5Bexchanges%5D%5B%5D=bitfinex&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=cryptobridge&factor%5Bexchanges%5D%5B%5D=cryptopia&factor%5Bexchanges%5D%5B%5D=hitbtc&factor%5Bexchanges%5D%5B%5D=poloniex&factor%5Bexchanges%5D%5B%5D=yobit&dataset=NVI&commit=Calculate"
    return url

# Handle 'whattomine' operation within the given --scope
def process_scope(self, config, coin):
    sttyColumns, maxRigNameLen = config.get_sttyColumnsMaxRigNameLen()
    maxRigNameLen += 3
    totals = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    actualMaxRslts = 0
    for key in sorted(config.ANSIBLE_HOSTS):
        host = config.ANSIBLE_HOSTS[key]
        if config.SCOPE.upper() == 'ALL' or config.SCOPE.upper() in host['hostname'].upper():
            if config.VERBOSE:
                maxRslts = len(totals)-1
            else:
                maxRslts = 4
            print(('%.'+str(maxRigNameLen)+'s')%('['+host['hostname']+']            '),end='')
            sys.stdout.flush()

            cmdLine = ['ssh', '-l', config.GLOBALS['MINERS_USER'], 
                       '-o', 'StrictHostKeyChecking=no', host['ip'], 'miners', 'whattomine']
            proc = subprocess.Popen(cmdLine, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            out, err = proc.communicate(None)
            if out:
                totIdx = 0
                for ln in out.decode().split('\n'):
                    ln = ln.rstrip()
                    coinStats = ln.split(',')
                    if len(coinStats) > 4:
                        print('%6s %5s %5s '%(coinStats[0],coinStats[1],coinStats[4]),end='')
                        totals[totIdx] += float(coinStats[1])
                        totIdx += 1
                        if totIdx > actualMaxRslts: actualMaxRslts = totIdx
                        maxRslts -= 1
                        if maxRslts <= 0:
                            break
            if err:
                for ln in err.decode().split('\n'):
                    ln = ln.rstrip()
                    if ln: print(ln+';',end='')
            print()

    print(('%.'+str(maxRigNameLen)+'s')%('TOTALS:                 '),end='')
    prev_total = totals[0]
    for idx in range(0,actualMaxRslts):
        diff = 1-(prev_total/totals[idx])
        print('       %3.2f  %3i%% '%(totals[idx],int(diff*100)),end='')
        prev_total = totals[idx]
    print()


def initialize(self, config, coin):
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    return config.ALL_MEANS_ONCE
