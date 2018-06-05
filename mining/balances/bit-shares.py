#!/usr/bin/python3
### Ref: http://docs.pybitshares.com/en/latest/bitshares.account.html
### Ref: https://www.dwheeler.com/essays/python3-in-python2.html
### Ref: http://pythonology.blogspot.com/2009/02/making-code-run-on-python-20-through-30.html
'''Instead of the version-specific except clause forms I use just 'except SomeException:' or 'except:' 
and then use sys.exc_info() inside the except block to get at the exception information. That returns 
a three-value tuple, the second element of which is the same thing you would get for 'e' in 
'except SomeException e:' or 'except SomeException as e|:'.
'''
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import os
import json
import sys

try:
     xrange = xrange
     # We have Python 2
except:
     xrange = range
     # We have Python 3

from bitshares.account import Account

miners_user_ssh = '/home/'+os.getenv('MINERS_USER')+'/.ssh/'
with open(miners_user_ssh + sys.argv[1].lower()+'.key') as secrets:
    secrets_json = json.load(secrets)
    secrets.close()

account = Account(secrets_json['account'])
print(account.balances)
