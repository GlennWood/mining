import os
import signal
import status
import start

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['COIN']+")")

    # We have this way of handing all this off to SystemD ...
    miner = coin['MINER']
    client = None
    if miner in config.SHEETS['Clients']:
        client = config.SHEETS['Clients'][miner]
        miner = client['EXECUTABLE']
    if miner in start.MINER_TO_BINARY: miner = start.MINER_TO_BINARY[miner]
    if miner.endswith('.service'):
        miner = miner.replace('.service','')
        cmd = 'sudo service '+miner+' stop'
        if config.DRYRUN:
            print cmd
        else:
            os.system(cmd)
        return 0
    

    pinfo = status.get_status(coin)
    if pinfo is None:
        print coin['COIN']+": There is no process mining "+coin['COIN']
        return 1
    else:
        if config.arguments['--dryrun']:
            print "sudo kill SIGKILL " + str(pinfo['pid'])
        else:
            try:
                os.kill(pinfo['pid'], signal.SIGKILL)
            except OSError:
                print "You must be root to stop this "+coin['COIN']+" miner; e.g. 'sudo kill SIGKILL " + str(pinfo['pid'])+"'"
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
    return 0

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['COIN']+")")
    return 0

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['COIN']+")")
    return 0
