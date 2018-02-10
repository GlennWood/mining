#!/usr/bin/python

### Ref: https://docs.python.org/2/howto/urllib2.html
import urllib2

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import re
import datetime
import os
import sys
import subprocess
DATA_DIR='../data/'

## This method is for invocation by monitor-miners.py
## cap_diff.py may be invoked from the command line, also
def process(self,config,arguments):
    if arguments.get('-v'): config.logger.info("CMD: python /opt/mining/monitor/cap_diff.py")
    proc = subprocess.Popen(['python', '/opt/mining/monitor/cap_diff.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = proc.communicate(None)
    config.logger.info(out)
    if err: 
        config.logger.error(err)
        return 1
    return 0


###
# Calculate string versions of today's and yesterday's dates
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
today = today.strftime("%Y%m%d")
yesterday = yesterday.strftime("%Y%m%d")

###
# Get today's CoinMarketCap report (or reuse one already downloaded)
todaysCoinmarketcapHtmlname = DATA_DIR+'coinmarketcap-'+today+'.html'
if not os.path.isfile(todaysCoinmarketcapHtmlname):
    print "Fetching " + todaysCoinmarketcapHtmlname
    response = urllib2.urlopen('https://coinmarketcap.com/all/views/all/')
    coinmarketcap = response.read()
    with open(todaysCoinmarketcapHtmlname, 'w') as f: f.write(coinmarketcap)

###
### Read today's XML file, or generate it if not done already
todaysCoinmarketcapXmlname = DATA_DIR+'coinmarketcap-'+today+'.xml'
if not os.path.isfile(todaysCoinmarketcapXmlname):
    print "Generating " + todaysCoinmarketcapXmlname
    with open(todaysCoinmarketcapHtmlname, 'r') as f: xmlStr = f.read()
    # Do some regex match and substitues to make the coinmarketcap HTML into valid XML
    regex = re.compile(r'.*?<table class="table js-summary-table" id="currencies-all".*?(<tbody>.*</tbody>)', re.DOTALL)
    match = regex.match(xmlStr)
    xmlStr = re.sub(r'data-supply-container', '', match.group(1))
    xmlStr = re.sub(r'png">', 'png"/>', xmlStr)
    with open(todaysCoinmarketcapXmlname, 'w') as f: f.write(xmlStr)
else:
    with open(todaysCoinmarketcapXmlname, 'r') as f: xmlStr = f.read()

print "Parsing " + todaysCoinmarketcapXmlname
xml = ET.fromstring(xmlStr)

print "Calculating difference between " + today + "'s and " + yesterday + "'s capitalization sequence."
todaysList = []
capsMap = {}
minableCount = 0
idx = 1
for coin in xml.findall("tr"):
    notMinable = coin.findall("td[@class='no-wrap text-right circulating-supply']")
    ### Argh; notMinable[0].text does not return the text, just always a bunch of spaces!
    notMinable = ET.tostring(notMinable[0], encoding='utf8', method='xml')
    if '*' in notMinable:
        continue
    minableCount += 1
    sym = coin.findall("td[@class='no-wrap currency-name']/span[@class='currency-symbol']/a")[0].text
    cap = coin.findall("td[@class='no-wrap market-cap text-right']")[0]
    cap = re.sub(r',','',re.sub(r'\s+[$]?', '', cap.text))
    todaysList.append(sym)
    capsMap[sym] = idx
    idx = idx + 1

###
# Write out today's capitalization list for later reference
with open(DATA_DIR+'results-'+today+'.lst', 'w') as lstfile:
    for sym in todaysList:
        lstfile.write(sym+"\n")
# Read yesterday's capitalization list for comparison
try:
    with open(DATA_DIR+'results-'+yesterday+'.lst', 'r') as f:
        yesterdaysList = f.read().splitlines()
except IOError as ex:
    print ex
    print "Run cap-diff again tomorrow, then we can calculate a difference."
    sys.exit(1)



###
# Now we get down to work!
threshold = 2
tIdx = 0
yIdx = 0
diffs = {}
moves = {}
while tIdx < len(todaysList) and yIdx < len(yesterdaysList): 
    if yesterdaysList[yIdx] in moves:
        diff = yIdx - moves[yesterdaysList[yIdx]] - len(moves)
        if diff > threshold:
            diffs[yesterdaysList[yIdx]] = diff
        del moves[yesterdaysList[yIdx]]
        yIdx += 1
    else:
        if todaysList[tIdx] != yesterdaysList[yIdx]:
            moves[todaysList[tIdx]] = tIdx
            tIdx += 1
        else:
            tIdx += 1
            yIdx += 1

###
# Print our results as a CSV file
resultFilename = DATA_DIR+'diffs-'+today+'-'+yesterday+'.csv' 
print 'Printing ' + resultFilename
with open(resultFilename, 'w') as f:
    for key, value in sorted(diffs.iteritems(), key=lambda(k,v): (-v,k)):
        f.write("%s,%s\n" % (key, value))

print("%i minable coins, %i have moved up more than %i\n" % (minableCount, len(diffs), threshold))
