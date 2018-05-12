import os
import sys
from gpustat import GPUStatCollection


def process(self, config, coin):

    postfix = '-'+coin['COIN']
    if config.ALL_COINS: postfix = ''

    gpu_stats = GPUStatCollection.new_query()
    idx = 0
    settings = 'sudo nvidia-settings -c :0'
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
            settings += ' -a "[gpu:'+str(idx)+']/GPUMemoryTransferRateOffset[3]='+str(int(oc))+'"'
            iuv = int(uv)
            if iuv in nvidia_pwrs:
                nvidia_pwrs[iuv].append(str(idx))
            else:
                nvidia_pwrs[iuv] = [str(idx)]
            idx += 1

    overclock_filename = os.getenv('LOG_RAMDISK','/var/local/ramdisk')+'/overclock-dryrun.sh'
    with open(overclock_filename, 'w') as fh: 
        for pwr in nvidia_pwrs:
            fh.write("sudo nvidia-smi -i "+','.join(nvidia_pwrs[pwr])+" -pl "+str(pwr))
            fh.write("\n")
        fh.write(settings)
        fh.write("\n")

    if config.DRYRUN:
        with open(overclock_filename, 'r') as fh:
            print(fh.read())
    else:
        with open(os.getenv('LOG_RAMDISK','/var/local/ramdisk')+'/overclock.sh', 'w') as fh: 
            for pwr in nvidia_pwrs:
                fh.write("sudo nvidia-smi -i "+','.join(nvidia_pwrs[pwr])+" -pl "+str(pwr))
        if config.VERBOSE: print(settings)
        os.system(settings)

    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    return config.ALL_MEANS_ONCE
