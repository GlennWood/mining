## Check monitor's status and exit
import subprocess

## if OPERATION=status, check monitor's status and exit
def process(self, config, arguments):
    cmd = '/usr/bin/tail -f /var/log/mining/monitor.log'
    if arguments.get('-X'):
        print cmd
    else:
        try:
            subprocess.call(['tail', '-f', '/var/log/mining/monitor.log'])
        except KeyboardInterrupt:
            if config.VERBOSE: print 'exit: monitor-miners logs /var/log/mining/monitor.log'
    return 0
