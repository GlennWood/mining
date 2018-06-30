import os.path
import status
import stat
import filecmp
import time
import sys
from pwd import getpwnam
try:
    from gpustat import GPUStatCollection
    GPUSTAT = True
except:
    GPUSTAT = False


def process(self, config, coin):
    # volatile means this operation make changes in settings
    VOLATILE = not config.DRYRUN and not config.QUERY
    
    postfix = '-'+coin['COIN']
    if config.ALL_COINS: postfix = ''

    if not config.FORCE and status.get_status(None) and VOLATILE:
        if not config.QUICK:
            print("A miner is currently running, so we are skipping overclocking (use -f to force).")
        return config.ALL_MEANS_ONCE

    gpu_stats = []
    try:
        gpu_stats = GPUStatCollection.new_query()
    except NameError as ex:
        print('NameError: Cannot load GPUStatCollection.')
        print(ex)
        print("To fix this, do 'pip3 install gpustat'.")
        return config.ALL_MEANS_ONCE
    except:
        if config.PLATFORM != 'AMD':
            print('Except: Cannot load GPUStatCollection on platform='+config.PLATFORM)
            ex = sys.exc_info()
            print(ex)
        elif not config.QUICK:
            ### TODO: https://github.com/GPUOpen-Tools/GPA/blob/master/BUILD.md
            print("'miners overclock' is not implemented for AMD devices")
        return config.ALL_MEANS_ONCE

    idx = 0
    xauthority = '/var/lib/lightdm/.Xauthority'
    settings = 'DISPLAY=:0 XAUTHORITY='+xauthority+' nvidia-settings -c :0'
    nvidia_pwrs = { }
    oper = '-a'
    if config.QUERY:
        if config.VERBOSE:
            oper = '-q'
        else:
            oper = '--terse -q'

    for gpu in gpu_stats:
        if gpu.uuid.upper() in config.SHEETS['Overclock']:
            dev = config.SHEETS['Overclock'][gpu.uuid.upper()]
            uv = dev['UV']             # default undervolt (or watts-limit)
            if 'UV'+postfix in dev:    # unless a coin-specific one is given
                uv = dev['UV'+postfix]
            oc = dev['OC']             # default overclock
            if 'OC'+postfix in dev:    # unless a coin-specific one is given
                oc = dev['OC'+postfix]
            if oc:
                settings += ' '+oper+' "[gpu:'+str(idx)+']/GPUMemoryTransferRateOffset[3]'
                if not config.QUERY: settings += '='+str(int(oc))
                settings += '"'
            if uv:
                iuv = int(uv)
                if iuv in nvidia_pwrs:
                    nvidia_pwrs[iuv].append(str(idx))
                else:
                    nvidia_pwrs[iuv] = [str(idx)]
            idx += 1

    overclock_dryrun = os.getenv('LOG_RAMDISK','/var/local/ramdisk')+'/overclock-dryrun.sh'
    with open(overclock_dryrun, 'w') as fh: 
        if not config.QUERY:
            fh.write("echo '%s %i %s'\n\n"%('Overclocking', len(gpu_stats), 'GPUs.'))
            fh.write('%s\n'%('sudo nvidia-smi -pm 1'))
        for pwr in nvidia_pwrs:
            if not config.QUERY:
                cmd = "sudo nvidia-smi -i "+','.join(nvidia_pwrs[pwr])+" -pl "+str(pwr)
                fh.write('%s\n'%(cmd))
                fh.write("\n")
                if config.VERBOSE: print(cmd)
        fh.write(settings)
        fh.write("\n")
        if config.VERBOSE: print(settings)
    os.chmod(overclock_dryrun, stat.S_IXUSR|stat.S_IXGRP | stat.S_IWUSR|stat.S_IWGRP | stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH)
    os.chown(overclock_dryrun, getpwnam(os.getenv('MINERS_USER')).pw_uid, -1)

    if config.DRYRUN:
        print("\nexport DISPLAY=:0\nexport XAUTHORITY="+xauthority+"\n")
        with open(overclock_dryrun, 'r') as fh:
            print(fh.read().replace('-a'," \\\n    -a"))
    else:
        overclock_filename = os.getenv('LOG_RAMDISK','/var/local/ramdisk')+'/overclock.sh'
        if VOLATILE and not config.FORCE and os.path.isfile(overclock_filename) and filecmp.cmp(overclock_dryrun, overclock_filename):
            timestamp = time.ctime(os.path.getctime(overclock_filename))
            if not config.QUICK and not config.QUERY:
                print("Overclock settings are identical to those already set at '"+timestamp+"', so we are keeping them (use -f to force).")
        else:
            os.rename(overclock_dryrun, overclock_filename)
            if config.VERBOSE:
                with open(overclock_filename, 'r') as fh:
                    print(fh.read())
            os.system("/bin/bash "+overclock_filename)

    if os.path.isfile(overclock_dryrun): os.remove(overclock_dryrun)
    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    return config.ALL_MEANS_ONCE
