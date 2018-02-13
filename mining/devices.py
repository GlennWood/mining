import subprocess
import re

def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['COIN']+")")
    #TODO os.system("lspci |grep 'VGA compatible controller'|grep -v 'Intel Corporation Device'")
    #TODO a much more interesting report:  lshw -c video
    
    devices = {}
    ### Scan for AMD devices' metrics using 'sensors'
    proc = subprocess.Popen(['sensors'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = proc.communicate(None)
    if err:
        print err
        return 1

    lines = out.splitlines()
    idx = 0
    while idx < len(lines):
        if 'amdgpu' in lines[idx]:
            key = lines[idx]
            regex = re.compile(r'.*?([+][0-9]*[.][0-9]*).*', re.DOTALL)
            match = regex.match(lines[idx+3])
            if match is not None: devices[key] = match.group(1)
            idx += 1
        else: idx += 1
    
    
    ### Scan for Nvidia devices' metrics using 'nvidia-smi'
    ### TODO: a simpler temperature report: nvidia-smi -q -d temperature
    try:
        proc = subprocess.Popen(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out, err = proc.communicate(None)
        #print out
        if err:
            print err
            return 1
        lines = out.splitlines()
        idx = 0
        for line in lines:
            if '%' in line:
                regex = re.compile(r'.*?%\s*([0-9]*)C.*', re.DOTALL)
                match = regex.match(line)
                if match is not None: devices['nvidia-'+str(idx)] = match.group(1)
                idx += 1
    except OSError as ex:
        if config.arguments.get('-v'): print str(ex)

    gpu_num = 0
    for device in sorted(devices):
        if 'amd' in device:
            print "GPU"+str(gpu_num)+" (AMD): pci="+device.replace('amdgpu-pci-','').replace('00','')+" "+devices[device]+'C'
        else:
            print device+": +"+devices[device]+'C'
        gpu_num += 1

    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize()")
    if coin: coin = coin
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize()")
    if coin: coin = coin
    return config.ALL_MEANS_ONCE
