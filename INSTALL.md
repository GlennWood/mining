Starting from an Ubuntu server
------------------------------

	export MINING_USER=$USER
	sudo -E su -p -
	[sudo] password for <MINERS_USER>: 
	cd /opt
	mkdir mining
	chown $MINERS_USER mining/
	
Get GlennWood/mining files
--------------------------

* Clone GlennWood/mining to `/opt/mining`.

        cd /opt/mining
	     apt -y install git
	     git clone https://github.com/GlennWood/miners.git
        chmod 0754 mining/install/install-* mining/install/*.{py,sh}

* Setup initial miners-user account

        /opt/mining/install/install-1st 
        > MINERS_USER account: <your-MINERS_USER>
        > <your-MINERS_USER> password: 
        > <your-MINERS_USER> password, again: 
 
 This script completes rather quickly.
 Then you need to run:
 
         /opt/mining/install/install-2nd
 
 which will take a bit longer. It will reboot your rig when it is done.

Install Nvidia drivers and CUDA
-------------------------------

If you are using Nvidia GPUs ...

1. Do the first phase of Nvidia driver install:

        cat >> /etc/environment << NVIDIA_CUDA_VERSIONS
        NVIDIA_VERSION=396.26
        CUDA_VERSION=9.2.88
        NVIDIA_CUDA_VERSIONS
        source /etc/environment
        
        $MINING_ROOT/install/install-nvidia-1st $NVIDIA_VERSION

2. `install-nvidia-1st` will reboot the rig. Follow that up with the second phase:

        $MINING_ROOT/install/install-nvidia-2nd
    which also reboots your rig when it is done.

3. Install CUDA 9.2.88

        $MINING_ROOT/install/install-cuda

4. Setup overclocking capability:

        $MINING_ROOT/install/overclock-1st
   This will reboot your rig when it is done (which is quick).

Install AMD Pro
-------------------------------

If you are using AMD GPUs ...

    $MINING_ROOT/install/install-amd-pro
    $MINING_ROOT/install/install-opencl
    $MINING_ROOT/install/install-GPUOpen-Tools