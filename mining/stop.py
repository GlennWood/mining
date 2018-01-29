import os
import signal
import status

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['Coin']+")")

    pinfo = status.get_status(coin)
    if pinfo is None:
        print coin['Coin']+": There is no process mining "+coin['Coin']
        return 1
    else:
        if config.arguments['--dryrun']:
            print "sudo kill SIGKILL " + str(pinfo['pid'])
        else:
            try:
                os.kill(pinfo['pid'], signal.SIGKILL)
            except OSError:
                print "You must be root to stop a miner; e.g. 'sudo kill SIGKILL " + str(pinfo['pid'])+"'"
            '''
Traceback (most recent call last):
  File "/usr/local/bin/miners", line 76, in <module>
    for OP in arguments['OPERATION'].split(','): exec_operation_method(OP, 'process')
  File "/usr/local/bin/miners", line 56, in exec_operation_method
    RC = method(module, config, config.coin_dict[ticker])
  File "/opt/mining/mining/stop.py", line 16, in process
    os.kill(pinfo['pid'], signal.SIGKILL)
OSError: [Errno 1] Operation not permitted
'''
    return None

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['Coin']+")")

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['Coin']+")")
    return 0
