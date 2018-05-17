import os.path
from gpustat import GPUStatCollection
import status
import stat
import filecmp
import time

def process(self, config, coin):

    postfix = '-'+coin['COIN']
    if config.ALL_COINS: postfix = ''

    if not config.FORCE and status.get_status(None):
        if not config.QUICK:
            print("A miner is currently running, so we are skipping overclocking (use -f to force).")
        return config.ALL_MEANS_ONCE

    try:
        gpu_stats = GPUStatCollection.new_query()     
    except:
        if not config.QUICK:
            ### TODO: https://github.com/GPUOpen-Tools/GPA/blob/master/BUILD.md
            print("'miners overclock' is not implemented for AMD devices")
        return config.ALL_MEANS_ONCE

    idx = 0
    settings = 'nvidia-settings -c :0'
    nvidia_pwrs = { }
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
                settings += ' -a "[gpu:'+str(idx)+']/GPUMemoryTransferRateOffset[3]='+str(int(oc))+'"'
            if uv:
                iuv = int(uv)
                if iuv in nvidia_pwrs:
                    nvidia_pwrs[iuv].append(str(idx))
                else:
                    nvidia_pwrs[iuv] = [str(idx)]
            idx += 1

    overclock_dryrun = os.getenv('LOG_RAMDISK','/var/local/ramdisk')+'/overclock-dryrun.sh'
    with open(overclock_dryrun, 'w') as fh: 
        fh.write('%s\n'%('nvidia-smi -pm 1'))
        for pwr in nvidia_pwrs:
            cmd = "nvidia-smi -i "+','.join(nvidia_pwrs[pwr])+" -pl "+str(pwr)
            fh.write('%s\n'%(cmd))
            fh.write("\n")
            if config.VERBOSE: print(cmd)
        fh.write(settings)
        fh.write("\n")
        if config.VERBOSE: print(cmd)
    os.chmod(overclock_dryrun, stat.S_IXUSR|stat.S_IXGRP | stat.S_IWUSR|stat.S_IWGRP | stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH)

    if config.DRYRUN:
        print("\nexport DISPLAY=:0\nexport XAUTHORITY=/var/run/lightdm/root/:0\n")
        with open(overclock_dryrun, 'r') as fh:
            print(fh.read().replace('-a'," \\\n    -a"))
    else:
        overclock_filename = os.getenv('LOG_RAMDISK','/var/local/ramdisk')+'/overclock.sh'
        if not config.FORCE and os.path.isfile(overclock_filename) and filecmp.cmp(overclock_dryrun, overclock_filename):
            timestamp = time.ctime(os.path.getctime(overclock_filename))
            if not config.QUICK:
                print("Overclock settings are identical to those already set at '"+timestamp+"', so we are keeping them.")
        else:
            os.rename(overclock_dryrun, overclock_filename)
            if config.VERBOSE:
                with open(overclock_filename, 'r') as fh:
                    print(fh.read())
            os.system("sudo /bin/bash "+overclock_filename)

    if os.path.isfile(overclock_dryrun): os.remove(overclock_dryrun)
    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    return config.ALL_MEANS_ONCE
