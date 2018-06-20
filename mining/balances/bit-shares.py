#!/usr/bin/env python3
### Ref: http://docs.pybitshares.com/en/latest/bitshares.account.html
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import os
import json
import sys

from bitshares.account import Account

miners_user_keys = '/home/'+os.getenv('MINERS_USER',os.getenv('USER'))
if not os.path.isdir(miners_user_keys): miners_user_keys = os.getenv('HOME')
miners_user_keys += '/.ssh/mining-keys/'
with open(miners_user_keys + sys.argv[1].lower()+'.key') as secrets:
    secrets_json = json.load(secrets)
    secrets.close()

account = Account(secrets_json['account'])
print(account.balances)
