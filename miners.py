#!/usr/bin/python

"""Usage: miners.py OPERATION [-vqrhgXP] [--gpus GPUS | --platform N] [--dryrun] [COIN] ...

Apply OPERATION to the mining of designated COINs w

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
  -q --quick   quick mode
  -X --dryrun  print the command, then exit
  -P --print   log the response of anything that is downloaded into
                 a local file (it's name will be listed on console)
"""

from __future__ import print_function
import os
import sys
import socket
sys.path.insert(0,'/opt/mining/mining')

import config
import importlib

### Ref: http://docopt.org/
### Ref: https://github.com/docopt/docopt
from docopt import docopt

config = config.Config(docopt(__doc__, argv=None, help=True, version=None, options_first=False))
arguments = config.arguments

### Verify that ticker exists, or that it is in the form "oldCoin:newCoin"
def tickerInCoinMiners(config, METH, ticker):

    if ticker in config.SHEETS['CoinMiners']:
        return config.SHEETS['CoinMiners'][ticker]
    
    if ticker.find(':') >= 0: # Is it "oldCoin:newCoin"?
        (oldCoin, newCoin) = ticker.split(':')
        if oldCoin not in config.SHEETS['CoinMiners']:
            if METH == 'initialize': # We want to print this only once
                print ("Coin '" + oldCoin + "' is unknown.", file=sys.stderr)
            return None
        if newCoin not in config.SHEETS['CoinMiners']:
            if METH == 'initialize': # We want to print this only once
                print ("Coin '" + newCoin + "' is unknown.", file=sys.stderr)
            return None
        return [config.SHEETS['CoinMiners'][oldCoin], config.SHEETS['CoinMiners'][newCoin]]
    else:
        if METH == 'initialize': # We want to print this only once
            print ("Coin '" + ticker + "' is unknown.", file=sys.stderr)
            return None
        
        # This is a convenient place to generate WORKER_NAME
        if config.SHEETS['CoinMiners'][ticker]['MINER'].strip():
            hostN = socket.gethostname()
            config.WORKER_NAME = ticker + '-miner-' + hostN[len(hostN)-1]

    return config.SHEETS['CoinMiners'][ticker]

###
### Iterate over all COINs (from commandline)
### Execute the given method (METH) of the given module (MOD)
def exec_operation_method(OP, METH):
    try:
        for ticker in arguments['COIN']:
            
            coin = tickerInCoinMiners(config, METH, ticker.upper())
            if coin is None:
                return False
            module =  importlib.import_module(OP)
            method = getattr(module, METH)
            RC = method(module, config, coin)
  
            if RC == config.ALL_MEANS_ONCE: break

    except AttributeError as ex:
        if config.VERBOSE: print(ex)
        print ("Module '"+OP+"' has no "+METH+"() method.", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt as ex:
        if config.VERBOSE: print(ex)
        print ("KeyboardInterrupt in '"+OP+":"+METH+"()' method.", file=sys.stderr)
        sys.exit(1)
    return True
##################################################################################


##################################################################################
### MAIN #########################################################################

OPS = arguments['OPERATION'].split(',')
# TODO: Idea - make 'miners <coin>' behave like 'miners status <coin>'

### Execute finalize() on each OPERATION/COIN
success = True
if success:
    for OP in OPS: success &= exec_operation_method(OP, 'initialize')
### Loop over all OPERATIONs, applying each to all COINs
if success:
    for OP in OPS: success &= exec_operation_method(OP, 'process')
### Execute finalize() on each OPERATION/COIN
if success:
    for OP in OPS: success &= exec_operation_method(OP, 'finalize')

### EOF ##########################################################################
