from __future__ import print_function
import six
from pynvml import NVMLError
import sys
import importlib

### FIXME: sometimes a rig ignores a gpu, and 'miners devices' ought to report that:
'''
albokiadt@rig-Borg1:~$ miners devices -v
NVI0: 53C 167W GeForce GTX 1070 Ti 
NVI1: 52C 169W GeForce GTX 1070 Ti 
NVI2: 49C 161W GeForce GTX 1070 Ti 
TOTAL: 497 watts
albokiadt@rig-Borg1:~$ lspci|grep VGA
00:02.0 VGA compatible controller: Intel Corporation Device 1902 (rev 06)
02:00.0 VGA compatible controller: NVIDIA Corporation Device 1b82 (rev a1)
03:00.0 VGA compatible controller: NVIDIA Corporation Device 1b82 (rev a1)
05:00.0 VGA compatible controller: NVIDIA Corporation Device 1b82 (rev a1)
06:00.0 VGA compatible controller: NVIDIA Corporation Device 1b82 (rev a1)
'''

def process(self, config, coin):

    devices = {}

    ### scan for AMD metrics using rocm-smi
    try:
        sys.path.append('/opt/rocm/bin')
        rocm_smi = importlib.import_module('rocm_smi')
        for device in sorted(rocm_smi.listDevices()):
            clock = rocm_smi.getCurrentClock(device, 'mem', 'freq')
            if clock is None:
                continue
            clock = clock.replace('Mhz','')
            temp = rocm_smi.getSysfsValue(device, 'temp')
            power = rocm_smi.getSysfsValue(device, 'power').split('.')[0]
            vbios = rocm_smi.getSysfsValue(device, 'vbios')
            gpuid = rocm_smi.getSysfsValue(device, 'id')
            fanspeed = rocm_smi.getFanSpeed(device)
            devices['AMD'+device[4:]] = [ str(temp).replace('.0',''), power, clock, vbios, fanspeed, gpuid ]
    except ImportError as ex:
        if config.PLATFORM == 'AMD' or config.PLATFORM == 'BTH':
            print('ImportError: '+str(ex),file=sys.stderr)
            print("             Try 'sudo apt-get -y install rocm-amdgpu-pro'",file=sys.stderr)
    except OSError as ex:
        if config.VERBOSE:
            if str(ex) and str(ex).find('[Errno 2] No such file or directory') < 0:
                print(ex,file=sys.stderr)
            else:
                print("Cannot discover AMD devices, since 'rocm-smi' is not installed. See 'install/install-amd-pro' for instructions.",file=sys.stderr)

    ### Scan for Nvidia using gpustats.GPUStatCollection
    gpu_stats = [ ]
    try:
        from gpustat import GPUStatCollection
        gpu_stats = GPUStatCollection.new_query()
        if config.VERBOSE:
            print(str(len(gpu_stats))+" Nvidia devices found.")
    #except NVMLError_GpuIsLost as ex:
    except NVMLError as ex:
        if str(ex) != 'Driver Not Loaded':
            print('FAIL: '+str(ex), file=sys.stderr)   
        elif ex.value == None or config.PLATFORM == 'NVI' or config.PLATFORM == 'BTH':
            pip = 'pip2'
            if six.PY3: pip = 'pip3'
            print("gpustat for Nvidia GPUs is not installed.\nUse '"+pip+" install gpustat' to install it.",file=sys.stderr)
    except:
        ex = sys.exc_info()
        print(ex,file=sys.stderr)

    idx = 0
    for gpu in gpu_stats:
        devices['NVI'+str(gpu.index)] = gpu
        idx += 1
    
    idxNVI = 0
    total_nvi_watts = 0
    total_amd_watts = 0
    for device in sorted(devices):
        if 'AMD' in device:
            dev = devices[device]
            verbose = ''
            if dev[1]:
                power = int(dev[1])
                total_amd_watts += power
                power = '%3iW '%(power)
            else:
                power = ' N/A '
            if dev[2]:
                speed = '%4iMhz'%(int(dev[2]))
            else:
                speed = '  N/A '
            if config.VERBOSE:
                verbose = ' ' + str(int(dev[4]))+'% ' + dev[3] + ' (' + dev[5] + ') '
            print(device+' '+dev[0]+'C '+power+speed+verbose)
        else:
            uuid = ''
            if config.VERBOSE:
                uuid = devices[device].uuid
            watts = devices[device].power_draw 
            if not watts: 
                strWatts = ' N/A' # Some GPUs (looking at you GTX 750) do not return power level
            else:
                strWatts = "%3sW" % (watts)
            print("%s: %2sC %4s %s %s" % (device,devices[device].temperature,strWatts,devices[device].name,uuid))
            if watts: 
                total_nvi_watts += int(watts)
            idxNVI += 1
    total_watts = total_nvi_watts + total_amd_watts
    if total_nvi_watts != 0 and total_nvi_watts != total_watts: print("TOTAL: "+str(total_nvi_watts)+' watts (NVI)')
    if total_amd_watts != 0 and total_amd_watts != total_watts: print("TOTAL: "+str(total_amd_watts)+' watts (AMD)')
    print("TOTAL: "+str(total_watts)+' watts')

    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    if coin: coin = coin
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    if coin: coin = coin
    return config.ALL_MEANS_ONCE
