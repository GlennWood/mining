import subprocess
import sys

### Ref: https://textbelt.com/#
### Ref: https://github.com/ksdme/py-textbelt


'''

sendtext () { curl http://textbelt.com/text -d number=5551113333 -d "message=$1";echo message sent; }

https://textbelt.com/

curl -X POST https://textbelt.com/text \
       --data-urlencode phone='6502799436' \
       --data-urlencode message='Hello world' \
       -d key=textbelt
curl https://textbelt.com/status/34181516508140866

'''

TEXTBELT_KEY='33ff033886383072e3e7e5402a7da3988dcb01b2Y6COAJsTjjNm9sK3w2ws86jDq'
TEXTBELT_PHN='6502799436'

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['Coin']+")")

    inp = sys.stdin.readlines()
    message = "\n".join(inp)
    
    proc = subprocess.Popen(['curl', '-X', 'POST', 'https://textbelt.com/text', \
           '--data-urlencode', 'phone='+TEXTBELT_PHN, \
           '--data-urlencode', "message='"+message+"'", '-d', 'key='+TEXTBELT_KEY], \
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    jsonStr, err = proc.communicate(None)
    
    print jsonStr
    if not err is None: print 'ERR: '+err
    
    return None

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['Coin']+")")

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['Coin']+")")
    return config.ALL_MEANS_ONCE
