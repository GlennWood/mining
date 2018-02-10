## Check monitor's status and exit
import os
import sys
sys.path.insert(0,'/opt/mining/mining')
sys.path.insert(0,'/opt/mining/monitor')
import status
import textmsg
import fibo_meter

global loopCount, fiboMeter
loopCount = 0
fiboMeter = fibo_meter.FiboMeter()

def process(self, config, arguments):
    global loopCount
    if config.VERBOSE: config.logger.info('mon_miners.process()')
    pInfos = status.get_status(None,[os.getpid()])
    if pInfos != None and len(pInfos) > 0:
        for pInfo in pInfos:
            config.logger.info(' '.join(pInfo.get('cmdline')))
    else:
        config.logger.error("There are no mining processes running at this time!")
        if fiboMeter.fibo_next(loopCount) and arguments.get('-t'):
            textmsg.send(os.getenv('HOSTNAME')+": Not mining!")
            return 1
    loopCount += 1;
    return 0
