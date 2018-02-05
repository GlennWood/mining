from __future__ import print_function

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['COIN']+")")
    print(coin['COIN']+": ")
    return 0

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['COIN']+")")

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['COIN']+")")
    return 0
