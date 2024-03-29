TroubleShooting
===============

1. `Version mismatch: this is the 'cffi' package version 1.11.5`

* Detail

        Exception: Version mismatch: this is the 'cffi' package version 1.11.5, located in '/usr/local/lib/python3.5/dist-packages/cffi/api.py'.  When we import the top-level '_cffi_backend' extension module, we get version 1.5.2, located in '/usr/lib/python3/dist-packages/_cffi_backend.cpython-35m-x86_64-linux-gnu.so'.  The two versions should be equal; check your installation.

* Solution

        root:~# mv /usr/lib/python3/dist-packages/_cffi_backend.cpython-35m-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/_cffi_backend.cpython-35m-x86_64-linux-gnu.so-1.5.2
        root:~# ln /usr/local/lib/python3.5/dist-packages/_cffi_backend.cpython-35m-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/_cffi_backend.cpython-35m-x86_64-linux-gnu.so

Your version numbers (python3.5? crypto-1.5.2?) may differ.

2. `AttributeError: module 'lib' has no attribute 'Cryptography_HAS_SSL_ST'`

* Detail

Installing some new modules with `pip` seems to mangle the `OpenSSL` installation.

* Solution

Thanks to [Kiran Karnad](https://www.linkedin.com/pulse/solution-attributeerror-module-object-has-attribute-sslstinit-karnad/), whose solution should work for you, too:

    sudo rm -rf /usr/local/lib/python*/dist-packages/OpenSSL/
    sudo apt -y install --reinstall python-openssl

3. "Stratum authentication failed"

* Detail

        rig-Motley:/opt/suprminer$ miners logs
        ==> /var/log/mining/M-RVN-miner.log <==
        [2018-06-30 17:58:59] Stratum authentication failed
        [2018-06-30 17:58:59] ...retry after 30 seconds

* Solution

Remember that some mining pools (e.g. `suprnova.cc`) require that you register each worker with them. Your worker's name can be read from your `miners status` report, e.g. `M-RVN-miner` below.

        rig-Motley:/opt/suprminer$ miners status
        RVN: [11972] ./ccminer -o stratum+tcp://rvn.suprnova.cc:6667 --algo=x16r -u albokiadt.M-RVN-miner -p {x} 

4. "AttributeError: module 'lib' has no attribute 'Cryptography_HAS_SSL_ST'"

* Detail

Self-explanatary, ain't it?

* Solution

        sudo pip3 install -U cryptography

5. `Xlib:  extension "GLX" missing on display ":0".
`

You might find this in `/etc/X11/xorg.conf`:

        Undefined Device "intel" referenced by ServerLayout "layout".

Somehow Xorg has registered your internal graphics (i.e.`intel`) into `xorg.conf`, which would be fine except that it has not completed it. This prevents a host of Nvidia operations from executing properly.

Simply remove the errant line and reboot.

        sudo sed -i.bak '/"intel"/d' /etc/X11/xorg.conf
        sudo reboot

Power connectors, risers, GPUs, PSUs
------------------------------------
... do not need to come all from coordinated PSUs, after all!
See [Connecting power to risers and GPUs](https://forum.z.cash/t/powering-6-pin-risers-with-6-pin-pcie-cable/27008/13)


TODO
====

A. Idea - filter special grep's to STDERR, e.g. Claymore's restarting message(s) and its warning, here,

         got incorrect share. If you see this warning often, make sure you did not overclock it too much!
         WATCHDOG: GPU 4 hangs in OpenCL call, exit
         NVML: cannot get current temperature, error 15
         Miner cannot initialize for 5 minutes, need to restart miner!
        /opt/suprminer/ccminer RVN: Cuda error in func 'cuda_check_cpu_setTarget' at line 41 : an illegal memory access was encountered.

B. This is too slow, needs a restart. Automate?

    18:45:25|ethminer|  Speed 319.85 Mh/s    gpu/0 26.58  gpu/1 26.67  gpu/2 26.76  gpu/3 26.67  gpu/4 26.76  gpu/5 26.76  gpu/6 26.49  gpu/7 26.58  gpu/8 26.58  gpu/9 26.67  gpu/10 26.76  gpu/11 26.58  [A203+3:R0+0:F0] Time: 00:40

C. Restart required:
  
    FIXME: RVN keeps failing this way
    rvn.log - [2018-06-22 14:08:59] GPU #2: an illegal memory access was encountered
    rvn.err - Cuda error in func 'cuda_check_cpu_setTarget' at line 41 : an illegal memory access was encountered.

D. Restart required:

    ==> /var/log/mining/S-ETH-miner.log <==
    GPU #2: GeForce GTX 1070 Ti, 8119 MB available, 19 compute units, capability: 6.1  (pci bus 12:0:0)
    GPU #3: GeForce GTX 1070, 8119 MB available, 15 compute units, capability: 6.1  (pci bus 13:0:0)
    Total cards: 4
    You can use "+" and "-" keys to achieve best ETH speed, see "FINE TUNING" section in Readme for details.
    Miner cannot initialize for 5 minutes, need to restart miner!
    NVML: cannot get current temperature, error 15
    NVML: cannot get current temperature, error 15

E. Only a reboot can fix this: 

    albokiadt@rig-Server:~$ miners status
    ETH: [1664] tclsh8.6 /usr/bin/unbuffer ./ethdcrminer64 -epool us-east.ethash-hub.miningpoolhub.com:20535 -ewal albokiadt.S-ETH-miner -eworker albokiadt.S-...
    ETH: [1665] ./ethdcrminer64 -epool us-east.ethash-hub.miningpoolhub.com:20535 -ewal albokiadt.S-ETH-miner -eworker albokiadt.S-ETH-miner -esm 2 -epsw {x} ...
    albokiadt@rig-Server:~$ miners stop eth
    albokiadt@rig-Server:~$ miners status  
    ETH: [1665] ./ethdcrminer64 -epool us-east.ethash-hub.miningpoolhub.com:20535 -ewal albokiadt.S-ETH-miner -eworker albokiadt.S-ETH-miner -esm 2 -epsw {x} ...
    albokiadt@rig-Server:~$ miners stop eth
    albokiadt@rig-Server:~$ miners status  
    ETH: [1665] ./ethdcrminer64 -epool us-east.ethash-hub.miningpoolhub.com:20535 -ewal albokiadt.S-ETH-miner -eworker albokiadt.S-ETH-miner -esm 2 -epsw {x} ...
    albokiadt@rig-Server:~$ kill -9 1665
    albokiadt@rig-Server:~$ miners status
    ETH: [1665] ./ethdcrminer64 -epool us-east.ethash-hub.miningpoolhub.com:20535 -ewal albokiadt.S-ETH-miner -eworker albokiadt.S-ETH-miner -esm 2 -epsw {x} ...
    albokiadt@rig-Server:~$ sudo kill -9 1665 
    albokiadt@rig-Server:~$ sudo kill  1665  
    albokiadt@rig-Server:~$ miners status    
    ETH: [1665] ./ethdcrminer64 -epool us-east.ethash-hub.miningpoolhub.com:20535 -ewal albokiadt.S-ETH-miner -eworker albokiadt.S-ETH-miner -esm 2 -epsw {x} ...

F.

    ==> /var/log/mining/T-RVN-miner.err <==
    Cuda error in func 'cuda_check_cpu_setTarget' at line 41 : an illegal memory access was encountered.

    ==> /var/log/mining/T-RVN-miner.log <==
    [2018-06-25 07:52:15] GPU #3: an illegal memory access was encountered

G. `NVML: cannot get current temperature, error 15`

It says to "please wait", but doesn't do anything to wait for.

    ==> /var/log/mining/M-ETH-miner.err <==

    ==> /var/log/mining/M-ETH-miner.log <==
    ETH: GPU0 31.080 Mh/s, GPU1 31.802 Mh/s, GPU2 0.000 Mh/s, GPU3 31.052 Mh/s
    ETH: 06/24/18-15:29:57 - New job from us-east.ethash-hub.miningpoolhub.com:20535
    ETH - Total Speed: 93.838 Mh/s, Total Shares: 95, Rejected: 0, Time: 00:59
    ETH: GPU0 31.009 Mh/s, GPU1 31.803 Mh/s, GPU2 0.000 Mh/s, GPU3 31.027 Mh/s
    NVML: cannot get current temperature, error 15
    NVML: cannot get current temperature, error 15
    WATCHDOG: GPU 2 hangs in OpenCL call, exit
    WATCHDOG: GPU 2 hangs in OpenCL call, exit
    NVML: cannot get current temperature, error 15
    Quit, please wait...

And `miners stop` and `kill` will not stop or kill the miner, and CPU usage is 100%!

    rig-Nvidia:~$ miners status
    ETH: [1722] tclsh8.6 /usr/bin/unbuffer ./ethdcrminer64 -epool us-east.ethash-hub.miningpoolhub.com:20535 -ewal albokiadt.N-ETH-miner -eworker albokiadt.N-ETH-...
    ETH: [1723] ./ethdcrminer64 -epool us-east.ethash-hub.miningpoolhub.com:20535 -ewal albokiadt.N-ETH-miner -eworker albokiadt.N-ETH-miner -esm 2 -epsw {x}  -al...
    rig-Nvidia:~$ miners stop eth
    rig-Nvidia:~$ miners status  
    ETH: [1723] ./ethdcrminer64 -epool us-east.ethash-hub.miningpoolhub.com:20535 -ewal albokiadt.N-ETH-miner -eworker albokiadt.N-ETH-miner -esm 2 -epsw {x}  -al...
    rig-Nvidia:~$ kill -9 1723
    rig-Nvidia:~$ miners status
    ETH: [1723] ./ethdcrminer64 -epool us-east.ethash-hub.miningpoolhub.com:20535 -ewal albokiadt.N-ETH-miner -eworker albokiadt.N-ETH-miner -esm 2 -epsw {x}  -al...
    rig-Nvidia:~$ kill 1723   
    rig-Nvidia:~$ miners status
    ETH: [1723] ./ethdcrminer64 -epool us-east.ethash-hub.miningpoolhub.com:20535 -ewal albokiadt.N-ETH-miner -eworker albokiadt.N-ETH-miner -esm 2 -epsw {x}  -al...

H. Failure evidence besides log data.

    rig-Motley:~$ miners devices
    gpustat for Nvidia GPUs is not installed.
    TOTAL: 0 watts
    albokiadt@rig-Motley:~$ nvidia-smi
    Unable to determine the device handle for GPU 0000:0C:00.0: GPU is lost.  Reboot the system to recover this GPU

I. "GPU is lost"

Here, a GPU is lost (it is no longer calculating hashes), but all other GPUs are still running fine.

    rig-Nvidia:~$ miners overclock --query    
    Except: Cannot load GPUStatCollection on platform=NVI
    (<class 'pynvml.NVMLError_GpuIsLost'>, NVMLError_GpuIsLost(15,), <traceback object at 0x7fb2e85d6f48>)
    
    rig-Nvidia:~$ nvidia-smi 
    Unable to determine the device handle for GPU 0000:01:00.0: GPU is lost.  Reboot the system to recover this GPU

J. "an illegal memory access was encountered."

    rig-Motley:/opt/suprminer$ miners logs rvn
    ==> /var/log/mining/M-RVN-miner.log <==
    [2018-06-30 18:47:52] GPU #2: EVGA GTX 1070, 8804.47 kH/s
    [2018-06-30 18:47:53] accepted: 226/226 (diff 0.037), 17.11 MH/s yes!
    [2018-06-30 18:48:00] Stratum difficulty set to 15.8258 (0.06182)
    [2018-06-30 18:48:04] x16r block 279129, diff 16896.290
    [2018-06-30 18:48:05] GPU #3: Gigabyte GTX 1070, 464.22 MH/s
    [2018-06-30 18:48:05] GPU #3: an illegal memory access was encountered
    [2018-06-30 18:48:05] GPU #1: driver shutting down
    [2018-06-30 18:48:05] GPU #2: EVGA GTX 1070, 462.70 MH/s
    [2018-06-30 18:48:05] GPU #2: driver shutting down
    [2018-06-30 18:48:05] GPU #0: aes_cpu_init driver shutting down
    
    ==> /var/log/mining/M-RVN-miner.err <==
    Cuda error in func 'cuda_check_cpu_setTarget' at line 41 : an illegal memory access was encountered.
    Cuda error in func 'cuda_check_cpu_setTarget' at line 41 : driver shutting down.
    Cuda error in func 'cuda_check_cpu_setTarget' at line 41 : driver shutting down.

K. `WARNING: Unable to use the nvidia-cfg library to query NVIDIA hardware.
`
Haven't figured this out, so cannot use my new GTX 1080Ti since it won't be recognized by Nvidia drivers when it's plugged in.

[This](https://devtalk.nvidia.com/default/topic/1031824/cuda-setup-and-installation/no-gui-ubuntu-16-04-4-4-0-119-generic-quadro-k5200-tesla-k40c-driver-version-387-26/) might help (probably not).

    root@rig-Power:~# sudo dmesg |grep NVRM
    [    1.238054] NVRM: loading NVIDIA UNIX x86_64 Kernel Module  396.26  Mon Apr 30 18:01:39 PDT 2018 (using threaded interrupts)
    [   12.180171] NVRM: Xid (PCI:0000:0c:00): 32, Channel ID 00000000 intr 80040000
    [   16.185746] NVRM: RmInitAdapter failed! (0x26:0xffff:1123)
    [   16.197194] NVRM: rm_init_adapter failed for device bearing minor number 1
    ...
    and lot's more

`nouveau` is removed.

    root@rig-Power:~# lsmod |grep -i nouv
    root@rig-Power:~#

`lspci` sees it.

	root@rig-Power:~# lspci | grep VGA
	01:00.0 VGA compatible controller: NVIDIA Corporation Device 1b81 (rev a1)
	0c:00.0 VGA compatible controller: NVIDIA Corporation Device 1b06 (rev a1)
	0d:00.0 VGA compatible controller: NVIDIA Corporation Device 1b81 (rev a1)
	0e:00.0 VGA compatible controller: NVIDIA Corporation Device 1b82 (rev a1)
	0f:00.0 VGA compatible controller: NVIDIA Corporation Device 1b82 (rev a1)
	root@rig-Power:~# 

`nvidia-smi -L` does not see it (and takes a long time to not see it).

	root@rig-Power:~# nvidia-smi -L
	GPU 0: GeForce GTX 1070 (UUID: GPU-ce1df382-1fb6-119e-5048-15c524f28cf8)
	GPU 1: GeForce GTX 1070 (UUID: GPU-701dd1b3-98d5-831d-2c29-631381e7adf3)
	GPU 2: GeForce GTX 1070 Ti (UUID: GPU-d2b65de5-f788-5516-4ce2-4d108f2366c3)
	GPU 3: GeForce GTX 1070 Ti (UUID: GPU-0547b4d4-3354-32a0-eb63-e6013ca68ab8)
	root@rig-Power:~# 
