from __future__ import print_function
import subprocess
import re
import six
GPUSTAT = True
try:
    from gpustat import GPUStatCollection
except:
    GPUSTAT = False
import sys
from pynvml import *

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

    ### Scan AMD debug data
    '''
    root@rig-19X:~# cat /sys/kernel/debug/dri/*/amdgpu_pm_info|grep 'GFX Clocks and Power:' -A9
    GFX Clocks and Power:
            2000 MHz (MCLK)
            300 MHz (SCLK)
            10.238 W (VDDC)
            16.0 W (VDDCI)
            39.18 W (max GPU)
            39.84 W (average GPU)
    
    GPU Temperature: 63 C
    GPU Load: 0 %

root@rig-19X:~# cat /sys/kernel/debug/dri/*/amdgpu_pm_info|grep 'GFX Clocks and Power:' -A9
GFX Clocks and Power:
        2000 MHz (MCLK)
        1411 MHz (SCLK)
        113.157 W (VDDC)
        16.0 W (VDDCI)
        143.58 W (max GPU)
        142.3 W (average GPU)

GPU Temperature: 70 C
GPU Load: 100 %

    $> rocm-smi
====================    ROCm System Management Interface    ====================
================================================================================
 GPU  Temp    AvgPwr   SCLK     MCLK     Fan      Perf    SCLK OD
  3   76.0c   144.222W 1411Mhz  2000Mhz  40.0%    auto      0%       
  1   48.0c   38.209W  300Mhz   2000Mhz  16.86%   auto      0%       
  4   74.0c   144.104W 1411Mhz  1750Mhz  21.96%   auto      0%       
  2   74.0c   147.244W 1411Mhz  1750Mhz  23.92%   auto      0%       
  0   N/A     N/A      N/A      N/A      0.0%     None      N/A      
================================================================================
====================           End of ROCm SMI Log          ====================
    '''
    
    # Use rocm-smi to scan for AMD metrics
    try:
        proc = subprocess.Popen(['rocm-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out, err = proc.communicate(None)
        if err:
            if config.VERBOSE: print("subprocess.Popen(['rocm-smi']) "+err)
        else:
            lines = out.decode().splitlines()
            for line in lines:
                # 'GPU  Temp    AvgPwr   SCLK     MCLK     Fan      Perf    SCLK OD'
                # ' 3   76.0c   144.222W 1411Mhz  2000Mhz  40.0%    auto      0%'
                regex = re.compile(r'\s*(\d\d*)\s*([0-9]*)[.][0-9]*c\s*([0-9]*)[.][0-9]*W\s*([0-9.]*)Mhz\s*([0-9.]*)Mhz\s*([0-9.]*)%(.*)')
                #([0-9.]*)c\s*([0-9.]*)W\s*([0-9.]*)Mhz\s*([0-9.]*)Mhz\s*([0-9.]*)%\s*(\S*)\s*([0-9.]*)c%.*', re.DOTALL)
                #regex = re.compile(r'\s*(\d{1-2})\s*([0-9.]*)c\s*([0-9.]*)W\s*([0-9.]*)Mhz\s*([0-9.]*)Mhz\s*([0-9.]*)%\s*(\S*)\s*([0-9.]*)c%.*', re.DOTALL)
                match = regex.match(line)
                if match is not None: 
                    devices['AMD'+str(match.group(1))] = [match.group(2),match.group(3),match.group(4),match.group(5),match.group(6)]#,match.group(3),match.group(4),match.group(5),match.group(6)]
            if config.VERBOSE:
                print(str(len(devices))+" AMD devices found.")
    except OSError as ex:
        if config.VERBOSE:
            if str(ex) and str(ex).find('[Errno 2] No such file or directory') < 0:
                print(ex)
            else:
                print("Cannot discover AMD devices, since 'rocm-smi' is not installed. See 'install/install-amd-pro' for instructions.")

    ### Scan for Nvidia using gpustats.GPUStatCollection
    gpu_stats = [ ]
    if GPUSTAT:
        try:
            gpu_stats = GPUStatCollection.new_query()     
            if config.VERBOSE:
                print(str(len(gpu_stats))+" Nvidia devices found.")
        #except NVMLError_GpuIsLost as ex:
        except NVMLError as ex:
            print ('FAIL: '+str(ex))
        except:
            ex = sys.exc_info()
            if ex.value == None or config.PLATFORM != 'AMD':
                print("gpustat for Nvidia GPUs is not installed.")
    elif config.VERBOSE:
        pip = 'pip2'
        if six.PY3: pip = 'pip3'
        print("Cannot discover Nvidia devices, since 'gpustat' is not installed. Use '"+pip+" install gpustat' to install it.",file=sys.stderr)

    idx = 0
    for gpu in gpu_stats:
        devices['NVI'+str(gpu.index)] = gpu
        idx += 1
    
    idxNVI = 0
    total_nvi_watts = 0
    total_amd_watts = 0
    for device in sorted(devices):
        if 'AMD' in device:
            print(device+' '+devices[device][0]+'C '+devices[device][1]+'W '+devices[device][3]+'Mhz')
            total_amd_watts += int(devices[device][1])
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
    if total_nvi_watts != 0: print("TOTAL: "+str(total_nvi_watts)+' watts (NVI)')
    if total_amd_watts != 0: print("TOTAL: "+str(total_amd_watts)+' watts (AMD)')
    print("TOTAL: "+str(total_nvi_watts+total_amd_watts)+' watts')

    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    if coin: coin = coin
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    if coin: coin = coin
    return config.ALL_MEANS_ONCE
