from __future__ import print_function
import sys
from bitshares.account import Account

### ###########################################################
# Fetch balances from any exchange based on bitshares.
# Ref: https://github.com/bitshares/python-bitshares/blob/master/docs/tutorials.rst

class BitSharesAccount():
    
    def __init__(self, accountName):
        
        self._amounts_ = { }
        try: # bitshares.account will work under Python3, but throw exception if Python2
            account = Account(accountName)
            # We add the balances and open-orders amounts, since we still own unfilled open-orders
            amounts = { }
            for balance in account.balances:
                ticker = balance.symbol.replace('BRIDGE.','')
                if ticker not in amounts: amounts[ticker] = 0
                amounts[ticker] += balance.amount
            for openorder in account.openorders:
                order = openorder['base']
                ticker = order.symbol.replace('BRIDGE.','')
                if ticker not in amounts: amounts[ticker] = 0
                amounts[ticker] += order.amount

            self._amounts_ = amounts
        
        except KeyboardInterrupt as ex:
            raise KeyboardInterrupt()
        
        except:
            ex = sys.exc_info()[0]
            print( "Exception in balances.balances_bit_shares(): "+str(ex), file=sys.stderr )

            
    @property
    def amounts(self):
        return self._amounts_