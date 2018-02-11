## Check monitor's status and exit
import os
import sys
sys.path.insert(0,'/opt/mining/mining')
sys.path.insert(0,'/opt/mining/monitor')
import status
import textmsg
from fibo_meter import FiboMeter

fiboMeter = FiboMeter(1,2,2)

def process(self, config, arguments):
    if config.VERBOSE: config.logger.info('mon_miners.process()')
    pInfos = status.get_status(None,[os.getpid()],['/usr/local/bin/monitor-miners'])
    if pInfos != None and len(pInfos) > 0:
        for pInfo in pInfos:
            config.logger.info(str(pInfo.get('pid'))+' '+' '.join(pInfo.get('cmdline')))
    else:
        config.logger.error("There are no mining processes running at this time!")
        if arguments.get('-t') and fiboMeter.next():
            textmsg.send(os.getenv('HOSTNAME')+": Not mining!")
            return 1
    return 0
