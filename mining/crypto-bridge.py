#!/usr/bin/python3
### Ref: http://docs.pybitshares.com/en/latest/bitshares.account.html
### Ref: https://www.dwheeler.com/essays/python3-in-python2.html
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

try:
     xrange = xrange
     # We have Python 2
except:
     xrange = range
     # We have Python 3

from bitshares.account import Account


with open('/etc/mining/crypto-bridge.key') as secrets:
    secrets_json = json.load(secrets)
    secrets.close()

account = Account(secrets['account'])
print(account.balances)
#print(account.openorders)
#for h in account.history():
#    print(h)
