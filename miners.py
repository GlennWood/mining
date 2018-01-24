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

from __future__ import print_function
import sys
sys.path.insert(0,'/opt/mining/mining')

import config
import importlib

### Ref: http://docopt.org/
### Ref: https://github.com/docopt/docopt
from docopt import docopt

config = config.Config(docopt(__doc__, argv=None, help=True, version=None, options_first=False))
arguments = config.arguments

ALL_MEANS_ONCE={'balances':1, 'textmsg':1}

###
### Iterate over all COINs (from commandline)
### Execute the given method (METH) of the given module (MOD)
def exec_operation_method(OP, METH):
    try:
        for ticker_ in arguments['COIN']:
            ticker = ticker_.upper()
            if ticker not in config.coin_dict:
                print ("Coin '" + ticker + "' is unknown.", file=sys.stderr)
                return False
            else:
  
                if config.coin_dict[ticker]['Miner'].strip(): 
                    config.WORKER_NAME = ticker + '-miner'
                module =  importlib.import_module(OP)
                method = getattr(module, METH)
                method(module, config, config.coin_dict[ticker])
      
                if OP in ALL_MEANS_ONCE: break

    except AttributeError:
        print ("Module '"+OP+"' has no "+METH+"() method.", file=sys.stderr)
        sys.exit(1)
        return False
    
    return True
##################################################################################


##################################################################################
### MAIN #########################################################################

### Execute finalize() on each COIN
for OP in arguments['OPERATION'].split(','): exec_operation_method(OP, 'initialize')

### Loop over all OPERATIONs, applying each to all COINs
for OP in arguments['OPERATION'].split(','): exec_operation_method(OP, 'process')

### Execute finalize() on each COIN
for OP in arguments['OPERATION'].split(','): exec_operation_method(OP, 'finalize')

### EOF ##########################################################################
