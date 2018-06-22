#!/bin/bash

# You must execute this at least once before you can start overclocking Nvidia cards.
# This sets up the Xorg/Nvidia config, which, for some bizarre reason, Nvidia drivers need in order to talk to Nvidia cards.

### Ref: https://gist.github.com/bsodmike/369f8a202c5a5c97cfbd481264d549e9

    if [[ $EUID -ne 0 ]]
    then
		echo "$0 requires elevated privileges."
		sudo -H $0 $*
		exit;
	fi

mkdir -p /etc/X11/xorg.conf.d/ 2>/dev/null
touch /etc/X11/xorg.conf.d/20-nvidia.conf 

#?nvidia-xconfig --enable-all-gpus
cp /usr/share/nvidia-$NVIDIA_VER/* /usr/share/nvidia/
mv /usr/share/nvidia/nvidia-application-profiles-${NVIDIA_VER}.${NVIDIA_SUB}-key-documentation /usr/share/nvidia/nvidia-application-profiles-key-documentation
mv /usr/share/nvidia/nvidia-application-profiles-${NVIDIA_VER}.${NVIDIA_SUB}-rc /usr/share/nvidia/nvidia-application-profiles-rc
nvidia-xconfig -a --allow-empty-initial-configuration --cool-bits=28 --use-display-device="DFP-0" --connected-monitor="DFP-0"

  echo "A reboot is recommended before trying any actual overclocking at this time."
  echo "Hit ctrl-C to abort the reboot."
  for cnt in {10..0}
  do
    echo -n -e "\rReboot in $cnt "
    sleep 1
  done
  echo -n -e   "\rRebooting ... "
  reboot
