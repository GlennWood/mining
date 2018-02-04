import subprocess

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

def send(self, config, message):
    global TEXTBELT_KEY
    global TEXTBELT_PHN
    proc = subprocess.Popen(['curl', '-X', 'POST', 'https://textbelt.com/text', \
       '--data-urlencode', 'phone='+TEXTBELT_PHN, \
       '--data-urlencode', "message='"+message+"'", '-d', 'key='+TEXTBELT_KEY], \
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    jsonStr, err = proc.communicate(None)

    if jsonStr is '': return 1
    if config.VERBOSE: print jsonStr
    if not err is None: print 'ERR: '+err
    
    return 0
