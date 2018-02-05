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
  
                if config.coin_dict[ticker]['MINER'].strip(): 
                    config.WORKER_NAME = ticker + '-miner'
                module =  importlib.import_module(OP)
                method = getattr(module, METH)
                RC = method(module, config, config.coin_dict[ticker])
      
                if RC == config.ALL_MEANS_ONCE: break

    except AttributeError as ex:
        if config.VERBOSE: print(ex)
        print ("Module '"+OP+"' has no "+METH+"() method.", file=sys.stderr)
        sys.exit(1)
    
    return True
##################################################################################


##################################################################################
### MAIN #########################################################################

OPS = arguments['OPERATION'].split(',')

### Execute finalize() on each OPERATION/COIN
for OP in OPS: exec_operation_method(OP, 'initialize')
### Loop over all OPERATIONs, applying each to all COINs
for OP in OPS: exec_operation_method(OP, 'process')
### Execute finalize() on each OPERATION/COIN
for OP in OPS: exec_operation_method(OP, 'finalize')

### EOF ##########################################################################
