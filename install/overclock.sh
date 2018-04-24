#!/bin/bash

### Ref: https://gist.github.com/bsodmike/369f8a202c5a5c97cfbd481264d549e9

mkdir -p /etc/X11/xorg.conf.d/ 2>/dev/null
touch /etc/X11/xorg.conf.d/20-nvidia.conf 

### TODO: undo Meltdown/Spectre fix; bring back 20% of the hashrate
### Ref: http://www.cryptobadger.com/2017/05/build-ethereum-mining-rig-faq/#kernal_update

#?nvidia-xconfig --enable-all-gpus
cp /usr/share/nvidia-$NVIDIA_VER/* /usr/share/nvidia/
mv /usr/share/nvidia/nvidia-application-profiles-${NVIDIA_VER}.${NVIDIA_PATCH}-key-documentation /usr/share/nvidia/nvidia-application-profiles-key-documentation
mv /usr/share/nvidia/nvidia-application-profiles-${NVIDIA_VER}.${NVIDIA_PATCH}-rc /usr/share/nvidia/nvidia-application-profiles-rc
nvidia-xconfig -a --allow-empty-initial-configuration --cool-bits=28 --use-display-device="DFP-0" --connected-monitor="DFP-0"
## reboot

# This squelches the annoying "Failed to connect to Mir" messagez
DISPLAY_ORIG=$DISPLAY
export DISPLAY=:0
export XAUTHORITY=/var/run/lightdm/root/:0

# Enable nvidia-smi settings so they are persistent the whole time the system is on.
nvidia-smi -pm 1

# Set the power limit for each card (note this value is in watts, not percent!
#
# Four (4) GeForce 1070's
GPUS='3,4,5,7'
nvidia-smi -i $GPUS -pl 125
# For ZCL-bminer - 470.77 Sol/s 253.16 Nonce/s
# So keep the OC=1350 and it runs longest at a very good hashrate (11% above whattomine's!)
OC_1070=1350
# Too many restarts (5-6 per hour) so reducing to 1300
export XAUTHORITY=/var/run/lightdm/root/:0
export DISPLAY=:0
OC_1070=1200
nvidia-settings -c :0 -a "[gpu:3]/GPUMemoryTransferRateOffset[3]=$OC_1070" -a "[gpu:4]/GPUMemoryTransferRateOffset[3]=$OC_1070" -a "[gpu:5]/GPUMemoryTransferRateOffset[3]=$OC_1070" -a "[gpu:7]/GPUMemoryTransferRateOffset[3]=$OC_1070"

# Eight (8) EVGA 1070 Titans (the Borg)
# Set the power limit for each card (note this value is in watts, not percent!
# 160 watts crashes with ZCL, but not with NICEHASH-ETHASH; curious ...

## Rig-19X
GPUS='0,1,2,3,4,5,6,7'
GPUS=0
sudo nvidia-smi -pm 1
sudo nvidia-smi -i $GPUS -pl 150
export XAUTHORITY=/var/run/lightdm/root/:0
export DISPLAY=:0
OC_1070TI=1300
nvidia-settings -c $DISPLAY \
                -a "[gpu:0]/GPUMemoryTransferRateOffset[3]=$OC_1070TI" \
                -a "[gpu:1]/GPUMemoryTransferRateOffset[3]=$OC_1070TI" \
                -a "[gpu:2]/GPUMemoryTransferRateOffset[3]=$OC_1070TI" \
                -a "[gpu:3]/GPUMemoryTransferRateOffset[3]=$OC_1070TI" \
                -a "[gpu:4]/GPUMemoryTransferRateOffset[3]=$OC_1070TI" \
                -a "[gpu:5]/GPUMemoryTransferRateOffset[3]=$OC_1070TI" \
                -a "[gpu:6]/GPUMemoryTransferRateOffset[3]=$OC_1070TI" \
                -a "[gpu:7]/GPUMemoryTransferRateOffset[3]=$OC_1070TI"



## Rig-EVGA
sudo nvidia-smi -pm 1
sudo nvidia-smi -i 0 -pl 250
sudo nvidia-smi -i 1,2 -pl 150
sudo nvidia-smi -i 3,4 -pl 100
# For ZCL-bminer - 540.40 Sol/s 288.41 Nonce/s
# It takes a minute for bminer to start up, and the hashrate gradually increases from there.
# It might be 10/15 minutes before bminer warms up ZCL to its fastest rate; from 133.77 to 292.95 to 387.76 to 443.16 to 501.74 to 529.74 (and crash)
# So keep the OC=1300 and it runs longest at a very good hashrate (13% above whattomine's!)
OC_1070TI=1300
nvidia-settings -c $DISPLAY -a "[gpu:0]/GPUMemoryTransferRateOffset[3]=$OC_1070TI" \
                            -a "[gpu:1]/GPUMemoryTransferRateOffset[3]=$OC_1070TI" \
                            -a "[gpu:2]/GPUMemoryTransferRateOffset[3]=$OC_1070TI" \
                            -a "[gpu:3]/GPUMemoryTransferRateOffset[3]=$OC_1070TI"

DISPLAY_ORIG=$DISPLAY


### AMD Ref: https://linuxconfig.org/overclock-your-radeon-gpu-with-amdgpu
# echo "5" > /sys/class/drm/card1/device/pp_mclk_od



### Ref: https://www.reddit.com/r/EtherMining/comments/6wsf7o/new_amd_blockchain_optimized_drivers_availible/
# "Got 0,7% improved hashrate with expanse DAG file and 7,6% with eth dag file "