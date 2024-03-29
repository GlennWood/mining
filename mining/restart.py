from __future__ import print_function
import os
import sys
import time
import overclock
import re
import stat

### FIXME: 'start' does not recognize PLATFORM 'BTH' or empty as acceptable for PLATFORM=NVI

# Write /var/local/persist/lastest-start.cmd for later reference
def write_latest_start_cmd(config, cmd, WORKER_NAME):
    if cmd.find('/var/log/mining') < 0:
        cmd += ' >/var/log/mining/'+WORKER_NAME+'.log' + ' 2>/var/log/mining/'+WORKER_NAME+'.err' + ' &'
    if config.DRYRUN:
        fileName = '/var/local/persist/lastest-start-dryrun.cmd'
    else:
        fileName = '/var/local/persist/lastest-start.cmd'
    if os.path.isfile(fileName): os.remove(fileName)
    with open(fileName, 'w') as fh:
        fh.write(cmd+"\n")
    os.chmod(fileName, stat.S_IXUSR|stat.S_IXGRP | stat.S_IWUSR|stat.S_IWGRP | stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH)



def process(self, config, coin):

    with open('/var/local/persist/lastest-start.cmd', 'r') as fh:  
        cmd = fh.read()
    cmd = cmd.rstrip()

    regex = re.compile(r'cd (.*?) ; (.*)')
    match = regex.match(cmd)
    cdDir = ''
    if match and match.lastindex is 2:
        cdDir = match.group(1)
        cmd = match.group(2)

    if config.DRYRUN:
        if cdDir:
            print('cd '+cdDir+' ; '+cmd)
        else:
            print(cmd)
        return config.ALL_MEANS_ONCE

    # Set overclocking for this coin
    if not config.QUICK:
        overclock.initialize(self, config, coin)
        overclock.process(self, config, coin)
        overclock.finalize(self, config, coin)

    try:
        if config.VERBOSE: print(cmd)
        # Fork this!
        newpid = os.fork()
        if newpid != 0:
            return config.ALL_MEANS_ONCE 
        config.I_AM_FORK = True # Do not loop to any more OPs in this fork.

        # Make sure we're in the right working directory for the miner
        if cdDir != None and cdDir.strip() != '': 
            try:
                os.chdir(cdDir)
            except OSError as ex:
                print("change directory to '"+cdDir+"' failed: %d (%s)" % (ex.errno, ex.strerror), file=sys.stderr)
                sys.exit(ex.errno)
        
        try: os.setsid()
        except OSError as ex:# 'fork of './ccminer' failed: 1 (Operation not permitted)' 
            newpid = newpid#  due to python's exception when you are already the group-leader ... 
        os.umask(0)
             
        os.system(cmd)

    except SystemExit as ex:
        print("Exiting")
    except OSError as ex:
        print("fork of '"+'miner restart'+"' failed: %d (%s)" % (ex.errno, ex.strerror), file=sys.stderr)
        sys.exit(1)
    except:
        print(sys.exc_info())
    return config.ALL_MEANS_ONCE


def initialize(self, config, coin):
    return config.ALL_MEANS_ONCE


def finalize(self, config, coin):
    return config.ALL_MEANS_ONCE
