from __future__ import print_function

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['Coin']+")")
    print(coin['Coin']+": ")
    return 0

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['Coin']+")")

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['Coin']+")")
    return 0
