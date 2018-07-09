from __future__ import print_function
from lxml import html
import sys
import requests
import subprocess
### Ref: http://python-future.org/compatible_idioms.html
from builtins import range

NicehashToTicker = { }

def process(self, config, coin):
    global NicehashToTicker
    SOURCES_YML = config.load_sources_yml()
    NicehashToTicker = SOURCES_YML['NICEHASH_TO_TICKER']

    if config.SCOPE:
        return process_scope(self,config, coin)

    url = None
    for key in config.SHEETS['WhatToMine']:
        if config.HOSTNAME.find(key.upper()) >= 0:
            url = self.generateUrl(config, key)
            break
    if not url:
        print("Cannot match this hostname='"+config.HOSTNAME+"' with any key in miners.xslx/WhatToMine spreadsheet.", file=sys.stderr)
        return 1
    
    response = requests.get(url)
    response.raise_for_status()
    tree = html.fromstring(response.content)
    wtmList = tree.xpath("/html/body/div[@class='container']/table[@class='table table-sm table-hover table-vcenter']/tbody/tr")
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
Generate the WhatToMine url from the URL cell, URL_PORT cmdline option, or by generating it from the Param declaration rows.
'''
def generateUrl(config, cKey):

    if config.URL_PORT and config.URL_PORT != 'calc':
        return config.URL_PORT

    column = config.SHEETS['WhatToMine'][cKey]
    if column['URL'] and not ( config.URL_PORT and config.URL_PORT == 'calc'):
        url = column['URL']
        if config.VERBOSE: print(url, file=sys.stderr)
    else:
        # Build query string from paramers in this rig's WhatToMine column
        query = [ ]
        for key, value in column.items():
            if key != 'URL' and key != 'Param' and value:
                query.append("%s=%s"%(key,value))
        url = 'https://whattomine.com/coins?utf8=%E2%9C%93&' + ('&'.join(query)) + '&commit=Calculate'

    if config.VERBOSE: print(url, file=sys.stderr)
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

            try:
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
            except KeyboardInterrupt:
                print("KeyboardInterrupt")

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
