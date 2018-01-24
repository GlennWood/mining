#!/usr/bin/python

"""Usage: miners.py OPERATION [-vqrhgXP] [--gpus GPUS | --platform N] [--dryrun] [COIN] ...

Process FILE and optionally apply correction to either left-hand side or
right-hand side.

Arguments:
  OPERATION  start | stop | status | list | logs
               (a comma-separated list of OPERATIONs)
  COIN       Coin's symbol; defaults to all
               (multiple COINs may be specified)

Options:
  --platform N 0=AMD, 1=Nvidia, 2=both [default: 2]
  --gpus GPUS  Comma separated list of GPU indexes

  -h --help
  -v           verbose mode
  -q           quiet mode
  -X --dryrun  print the command, then exit
  -P --print   log the response of anything that is downloaded into
                 a local file (it's name will be listed on console)
"""

import sys
sys.path.insert(0,'/opt/mining/mining')

import mining.config
import mining.list
import mining.start
import mining.stats
import mining.status
import mining.balances
import mining.textmsg

### Ref: http://docopt.org/
### Ref: https://github.com/docopt/docopt
from docopt import docopt
import os
import psutil
import signal
import re
import urllib2
import json
import subprocess

import datetime
#import pandas as pd


config = mining.config.Config(docopt(__doc__, argv=None, help=True, version=None, options_first=False))
arguments = config.arguments

ALL_MEANS_ONCE={'balances':1, 'textmsg':1}


##################################################################################
### MAIN #########################################################################

### Loop over all OPERATIONs, applying each to all COINs
for OP in arguments['OPERATION'].split(','):
  try:
    for ticker_ in arguments['COIN']:
      ticker = ticker_.upper()
      if ticker not in config.coin_dict:
        print "Coin '" + ticker + "' is unknown."
      else:
  
        if config.coin_dict[ticker]['Miner'].strip(): 
  
          config.WORKER_NAME = ticker + '-miner'
          module = __import__(OP)
          method = getattr(module, 'process')
          method(module, config, config.coin_dict[ticker])
  
          if OP in ALL_MEANS_ONCE: break

  except AttributeError:
    print "Module '"+OP+"' has no process() method."
    sys.exit(1)


### Repeat that loop, to finalize each process
for OP in arguments['OPERATION'].split(','):

  try:
    for ticker_ in arguments['COIN']:
      ticker = ticker_.upper()
      if ticker in config.coin_dict:
        config.WORKER_NAME = ticker + '-miner'
        module = __import__(OP)
        method = getattr(module, 'finalize')
        method(module, config, config.coin_dict[ticker])
 
      if OP in ALL_MEANS_ONCE: break

  except AttributeError:
    if VERBOSE: print "Module '"+OP+"' has no finalize() method."

### EOF ##########################################################################
