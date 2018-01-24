
import config
import os

def process(self, config, coin):
  if config.TAIL_LOG_FILES:
    config.TAIL_LOG_FILES += ' ' + '/var/log/mining/'+config.WORKER_NAME+'.log' + ' /var/log/mining/'+config.WORKER_NAME+'.err'
  else:
    config.TAIL_LOG_FILES = '/var/log/mining/'+config.WORKER_NAME+'.log' + ' /var/log/mining/'+config.WORKER_NAME+'.err'

  return 0

def finalize(self, config, coin):
  if config.TAIL_LOG_FILES != '': os.system(config.DRYRUN+'tail -f ' + config.TAIL_LOG_FILES)
  return 0
