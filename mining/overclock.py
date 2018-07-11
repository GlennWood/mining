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
import yaml

global OverclockConfig

### #############################################################
def process(self, config, coin, quiet=False):
    global OverclockConfig
    # volatile means this operation make changes in settings
    VOLATILE = not config.DRYRUN and not config.QUERY
    
    postfix = '-'+coin['COIN']
    if config.ALL_COINS: postfix = ''

    if not config.FORCE and not config.DRYRUN and status.get_status(None) and VOLATILE:
        if not config.QUICK and not quiet:
            print("A miner is currently running, so we are skipping overclocking (use -f to force).")
        return config.ALL_MEANS_ONCE

    gpu_stats = []
    try:
        gpu_stats = GPUStatCollection.new_query()
    except NameError as ex:
        print('NameError: Cannot load GPUStatCollection.')
        print(ex)
        print("To fix this, do 'pip3 install gpustat'.")
        if not config.DRYRUN:
            return config.ALL_MEANS_ONCE
        
    except:
        if not config.DRYRUN:
            if config.PLATFORM != 'AMD' and not quiet:
                print('Except: Cannot load GPUStatCollection on platform='+config.PLATFORM)
                ex = sys.exc_info()
                print(ex)
            elif not config.QUICK and not quiet:
                ### TODO: https://github.com/GPUOpen-Tools/GPA/blob/master/BUILD.md
                print("'miners overclock' is not implemented for AMD devices")
            return config.ALL_MEANS_ONCE

    normalizedDevices = read_overclock_yml()
    sudo_nvidia_settings = get_sudo_nvidia_settings(config)

    xauthority = '~/.Xauthority'
    if sudo_nvidia_settings: xauthority = '/var/lib/lightdm/.Xauthority'
    settings = 'DISPLAY=:0 XAUTHORITY='+xauthority+' '+sudo_nvidia_settings+'nvidia-settings -c :0'
    nvidia_pwrs = { }
    oper = '-a'
    if config.QUERY:
        if config.VERBOSE:
            oper = '-q'
        else:
            oper = '--terse -q'
    
    for gpu in gpu_stats:
        if gpu.uuid in normalizedDevices:
            dev = normalizedDevices[gpu.uuid]
            oc = dev.get('OverClock',{})              # default undervolt (e.g. power-limit),
            oc = oc.get(coin['COIN'], oc.get('___','0,150')) # unless a coin-specific one is given
            oc, uv = oc.split(',')

        # old-way, deprecated until we've migrated all into conf/overclock.yml, then will be removed
        elif gpu.uuid.upper() in config.SHEETS['Overclock']:
            dev = config.SHEETS['Overclock'][gpu.uuid.upper()]
            uv = dev['UV']             # default undervolt (or watts-limit)
            if 'UV'+postfix in dev:    # unless a coin-specific one is given
                uv = dev['UV'+postfix]
            oc = dev['OC']             # default overclock
            if 'OC'+postfix in dev:    # unless a coin-specific one is given
                oc = dev['OC'+postfix]

        if oc:
            settings += ' '+oper+' "[gpu:'+str(gpu.index)+']/GPUMemoryTransferRateOffset[3]'
            if not config.QUERY: settings += '='+str(int(oc))
            settings += '"'
        if uv:
            iuv = int(uv)
            if iuv in nvidia_pwrs:
                nvidia_pwrs[iuv].append(str(gpu.index))
            else:
                nvidia_pwrs[iuv] = [str(gpu.index)]

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
    if os.getenv('MINERS_USER'):
        os.chown(overclock_dryrun, getpwnam(os.getenv('MINERS_USER')).pw_uid, -1)

    if config.DRYRUN:
        print("\nexport DISPLAY=:0\nexport XAUTHORITY="+xauthority+"\n")
        with open(overclock_dryrun, 'r') as fh:
            print(fh.read().replace('-a'," \\\n    -a"))
    else:
        overclock_filename = os.getenv('LOG_RAMDISK','/var/local/ramdisk')+'/overclock.sh'
        if VOLATILE and not config.FORCE and os.path.isfile(overclock_filename) and filecmp.cmp(overclock_dryrun, overclock_filename):
            if not config.QUICK and not config.QUERY:
                timestamp = time.ctime(os.path.getctime(overclock_filename))
                print("Overclock settings are identical to those already set at '"+timestamp+"', so we are keeping them (use -f to force).")
        else:
            os.rename(overclock_dryrun, overclock_filename)
            os.system("/bin/bash "+overclock_filename)
        if config.VERBOSE:
            with open(overclock_dryrun, 'r') as fh:
                print(fh.read())

    if os.path.isfile(overclock_dryrun): os.remove(overclock_dryrun)
    return config.ALL_MEANS_ONCE

### #############################################################
def read_overclock_yml():
    global OverclockConfig
    overclock_filename = '/opt/mining/conf/overclock.yml'
    if os.path.isfile(overclock_filename):
        with open(overclock_filename, 'r') as stream:
            try:
                OverclockConfig = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                OverclockConfig = { 'DEVICES': {}, 'RIGS': {} }

    overclockDevices = OverclockConfig['DEVICES']
    normalizedDevices = { }
    for key, val in overclockDevices.items():
        normalizedDevices[key] = val
        if 'Cohorts' in val:
            for cohort in val['Cohorts']:
                normalizedDevices[cohort] = val

    # Rignames (i.e. hostnames) are case-insensitive
    rigs = {}
    for key, val in OverclockConfig['RIGS'].items():
        rigs[key.upper()] = val
    OverclockConfig['RIGS'] = rigs
    
    return normalizedDevices

### #########################################################################################
# For some as yet unknown reason, some rigs can overclock as MINING_USER, while others must
# use sudo; until we figure that out (something to do with Xorg), we'll adapt to it this way.
def get_sudo_nvidia_settings(config):
    global OverclockConfig
    sudo_nvidia_settings = OverclockConfig.get('RIGS',{}).get(config.HOSTNAME,{}).get('sudo-nvidia-settings', False)
    if sudo_nvidia_settings:
        sudo_nvidia_settings = 'sudo '
    else:
        if os.geteuid() == 0:
            sudo_nvidia_settings = 'sudo -u '+os.getenv('MINERS_USER')+' '
        else:
            sudo_nvidia_settings = ''
    return sudo_nvidia_settings

### #############################################################
def initialize(self, config, coin):
    return config.ALL_MEANS_ONCE

### #############################################################
def finalize(self, config, coin):
    return config.ALL_MEANS_ONCE
