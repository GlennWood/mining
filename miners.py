#!/usr/bin/python

"""Usage: miners.py OPERATION [-fghlqrXPv] [--gpus GPUS | --platform typ] [--url-port UL] 
                [--scope scope] [--force] [--dryrun] [COIN] ...

Apply OPERATION to the mining of designated COINs w

Arguments:
  OPERATION  start | stop | swap | status | list | logs | et.al.
               (a comma-separated list of OPERATIONs)
  COIN       Coin's symbol; defaults to all
               (multiple COINs may be specified)

Options:
  --platform typ  AMD, NVI, BTH [default: BTH]
  --gpus GPUS   Comma separated list of GPU indexes
  --url-port UL replace miners.xslx's URL_PORT value with UL
  --scope scope list of rigs to operate on, or ALL

  -f --force   force execution, ignoring non-critical warnings
  -l           do not truncate lines longer than console width

  -h --help
  -v           verbose mode
  -q --quick   quick mode
  -X --dryrun  print the command, then exit
  -P --print   log the response of anything that is downloaded into
                 a local file (it's name will be listed on console)
"""

from __future__ import print_function
import sys

import config
import importlib

### Ref: http://docopt.org/
### Ref: https://github.com/docopt/docopt
from docopt import docopt

config = config.Config(docopt(__doc__, argv=None, help=True, version=None, options_first=False))
arguments = config.arguments

### Verify that ticker exists, or that it is in the form "oldCoin:newCoin"
def tickerInCoinMiners(config, METH, ticker, OP):

    if OP in ['balances']:
        return ''

    # This is a convenient moment to generate WORKER_NAME
    config.workerName(ticker)

    coin = config.findTickerInPlatformCoinMiners(ticker,)
    if coin:
        return coin
    
    if ticker.find(':') >= 0: # Is it "oldCoin:newCoin"?
        (oldCoin, newCoin) = ticker.split(':')
        if not config.findTickerInCoinMiners(oldCoin, METH == 'initialize'):
            return None
        if not config.findTickerInPlatformCoinMiners(newCoin, METH == 'initialize'):
            if METH == 'initialize': # We want to print this only once
                print ("Coin '" + newCoin + "' is unknown.", file=sys.stderr)
            return None
        return [config.SHEETS['CoinMiners'][oldCoin], config.SHEETS['CoinMiners'][newCoin]]
    else:
        coin = config.findTickerInCoinMiners(ticker, METH == 'initialize')
        # TODO check that this general miner is applicable to this PLATFORM
        if coin: return coin

    return None

###
### Iterate over all COINs (from commandline)
### Execute the given method (METH) of the given module (MOD)
def exec_operation_method(OP, METH):
    try:
        for ticker in arguments['COIN']:
            if config.I_AM_FORK: break

            coin = tickerInCoinMiners(config, METH, ticker.upper(), OP)
            if coin is None:
                return False
            module =  importlib.import_module(OP)
            method = getattr(module, METH)
            RC = method(module, config, coin)
  
            if RC == config.ALL_MEANS_ONCE: break
            if RC != 0: return False

    except ImportError as ex:
        if config.VERBOSE: print(ex)
        print ("Unknown operation '"+OP+"'.", file=sys.stderr)
        sys.exit(1)        
    except KeyboardInterrupt as ex:
        if config.VERBOSE: print(ex)
        print ("KeyboardInterrupt in '"+OP+":"+METH+"()' method.", file=sys.stderr)
        sys.exit(1)
    return True
##################################################################################


##################################################################################
### MAIN #########################################################################

### Execute finalize() on each OPERATION/COIN
success = True
if success:
    for OP in config.OPS: success &= exec_operation_method(OP, 'initialize')
### Loop over all OPERATIONs, applying each to all COINs
if success:
    for OP in config.OPS: success &= exec_operation_method(OP, 'process')
### Execute finalize() on each OPERATION/COIN
if success: 
    for OP in config.OPS: success &= exec_operation_method(OP, 'finalize')

sys.exit(config.RC_MAIN)

### EOF ##########################################################################
