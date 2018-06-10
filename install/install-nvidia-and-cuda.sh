#!/bin/bash

### TODO: Let's try this one next time; it looks promising!
###       Ref: https://www.pugetsystems.com/labs/hpc/The-Best-Way-To-Install-Ubuntu-16-04-with-NVIDIA-Drivers-and-CUDA-1097/

  if [[ $EUID -ne 0 ]]; then
    echo "$0 must be run as root."
    sudo $0 $*
    exit $?
  fi

  NVIDIA_VERSION=387.26
  CUDA_VERSION=9.2.88
  
  ### Note: Must be done in this order; even though both come from Nvidia
  ###       and both operate to some extent against (as in opposed to) the
  ###       other, doing it in this sequence works best; do not reverse.
  $MINING_ROOT/install/install-nvidia $NVIDIA_VERSION
  $MINING_ROOT/install/install-cuda   $NVIDIA_VERSION $CUDA_VERSION

  exit


### This version from Ref: https://github.com/BMische/eth.sh
### WARNING! A DANGEROUS SCRIPT IF IT DOESN'T WORK RIGHT!!! MIGHT REBOOT CONTINUOUSLY!!!!
# check for Ubuntu 16.04

    if [ -e /tmp/.os_check ]
    then
        :
    elif [[ "$(uname -v)" =~ .*16.* ]]
    then 
        touch /tmp/.os_check
    else
        printf "%s\n" "Ubuntu 16.04 not found, exiting..."
        exit 
    fi


# set file descriptors for verbose actions, catch verbose on second pass

    exec 3>&1
    exec 4>&2
    exec 1>/dev/null
    exec 2>/dev/null

    if [ -e /tmp/.verbose ]
    then
        exec 1>&3
        exec 2>&4
    fi 
   

# parsing command line options

    cuda_toolkit=0
    cuda_toolkit_version=9.1
    cuda_toolkit_patch=64
    driver_version="387"
    driver_patch="111"
    skip_action="false"
    

    while [ $# -gt 0 ]
    do 
        case $1 in
        -h)   cat >&3 <<HELP

USAGE: install-nvidia-and-cuda.sh [options]
         -v       enable verbose mode, lots of output
         -h       print this menu
         -c       install CUDA $cuda_toolkit_version toolkit
         -o       overclocking only
         -w WAL   wallet address (ETH)

EXAMPLE: sudo $0 -v

HELP
              exit 1
              ;;
        -v)   exec 1>&3
              exec 2>&4
              touch /tmp/.verbose
              ;;
        -o)   skip_action="true"
              ;;
        -c)   cuda_toolkit=1 
              ;;
        -w)   printf "%s" "$2" 1>&3 2>&4 > /tmp/.wallet_provided
              shift
              ;; 
        --)   shift
              break
              ;;           
        *)    printf "%s\n" "$1: unrecognized option" 1>&3 2>&4
              exit
              ;;        
        esac

        shift
    done

# setting up permissions and files for automated second and/or third run

    
    if [ -e /tmp/.autostart_complete ] || [ "$skip_action" = "true" ]
    then
        :
    else
        read -d "\0" -a user_array < <(who)
        printf "%s\n" "${user_array[0]} ALL=(ALL:ALL) NOPASSWD:/usr/bin/gnome-terminal" 1>&3 2>&4 >> /etc/sudoers
        cp "$(readlink -f $0)" /usr/local/sbin/install-nvidia-and-cuda.sh
        chmod a+x /usr/local/sbin/install-nvidia-and-cuda.sh 
        if [ -d "/home/${user_array[0]}/.config/autostart/" ] || mkdir -p "/home/${user_array[0]}/.config/autostart/"
        then           
             printf "%s\n%s\n%s\n%s" "[Desktop Entry]" "Name=install-nvidia-and-cuda" \
             "Exec=sudo /usr/bin/gnome-terminal -e /usr/local/sbin/install-nvidia-and-cuda.sh" \
             "Type=Application" 1>&3 2>&4 > /home/${user_array[0]}/.config/autostart/install-nvidia-and-cuda.desktop

             printf "%s\n%s\n" "[Desktop Entry]" "Name=lock" \
             'Exec=/usr/bin/gnome-terminal -e "gnome-screensaver-command -l"' \
             "Type=Application" 1>&3 2>&4 > /home/${user_array[0]}/.config/autostart/lock.desktop
             touch /tmp/.autostart_complete
        fi                       
    fi 

    if [ -e /tmp/.auto_login_complete ] || [ "$skip_action" = "true" ]
    then
        :
    else
        printf "%s\n%s\n%s" "[SeatDefaults]" "autologin-user=${user_array[0]}" "autologin-user-timeout=0" 1>&3 2>&4 > /etc/lightdm/lightdm.conf.d/autologin.conf
        touch /tmp/.auto_login_complete 
    fi
    
    
 
    

# Grabbing materials

    if [ -e /tmp/.materials_complete ] || [ "$skip_action" = "true" ]
    then
        :
    else
        printf "%s\n" "Grabbing some materials for later use ..." 1>&3 2>&4
        add-apt-repository -y "ppa:graphics-drivers/ppa" 
        add-apt-repository -y "ppa:ethereum/ethereum"
        apt-get -y install software-properties-common 
        mkdir /tmp/setupethminer
        cd /tmp/setupethminer
        wget "http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_${cuda_toolkit_version}.${cuda_toolkit_patch}-1_amd64.deb" 
        dpkg -i cuda-repo-ubuntu1604_${cuda_toolkit_version}.${cuda_toolkit_patch}-1_amd64.deb 
        wget "https://github.com/ethereum-mining/ethminer/releases/download/v0.11.0rc1/ethminer-0.11.0rc1-Linux.tar.gz" 
        tar -xvzf ethminer-0.11.0rc1-Linux.tar.gz 
        apt-get update 
        printf "%s\n" "Done..." 1>&3 2>&4
        touch /tmp/.materials_complete 
    fi
    

# check for Nvidia driver

    if [ -e /tmp/.driver_complete ] || [ "$skip_action" = "true" ]
    then
        :
    elif nvidia-smi 
    then
        printf "%s\n" "Nvidia driver found ..." 1>&3 2>&4
        printf "%s\n" "Generating xorg config with cool-bits enabled" 1>&3 2>&4
        nvidia-xconfig 
        nvidia-xconfig --cool-bits=8 
        touch /tmp/.driver_complete
        printf "%s\n" "Done, system will reboot in 10 seconds..." 1>&3 2>&4
        printf "%s\n" "This will continue automatically upon reboot..." 1>&3 2>&4           
        sleep 10s
        systemctl reboot        
    else
        printf "%s\n" "Grabbing driver, this may take a while..." 1>&3 2>&4
        apt-get -y --allow-unauthenticated install "nvidia-$driver_version" 
        touch /tmp/.driver_complete
        printf "%s\n" "Done, system will reboot in 10 seconds..." 1>&3 2>&4
        printf "%s\n" "This will continue automatically upon reboot..." 1>&3 2>&4
        sleep 10s
        systemctl reboot
    fi
            
                      
 # get CUDA toolkit

    if [ -e /tmp/.cuda_toolkit_complete ] || [ "$skip_action" = "true" ]
    then
        :
    elif [ $cuda_toolkit -eq 1 ]
    then
        # Cuda compilation tools, release 9.1, V9.1.85
        if nvcc -V | grep "release $cuda_toolkit_version" 
        then
            printf "%s\n" "CUDA toolkit $cuda_toolkit_version already installed..." 1>&3 2>&4
            touch /tmp/.cuda_toolkit_complete
        else
            printf "%s\n" "Getting CUDA $cuda_toolkit_version toolkit, this may take a really long time..." 1>&3 2>&4
            apt-get -y install cuda 
            export PATH=/usr/local/cuda-$cuda_toolkit_version/bin${PATH:+:${PATH}}
            printf "%s\n" "Done..." 1>&3 2>&4
            touch /tmp/.cuda_toolkit_complete
        fi
    fi
          

# get ethminer
    
    if [ -e /tmp/.ethminer_complete ] || [ "$skip_action" = "true" ]
    then
         :
    else
        printf "%s\n" "Installing CUDA optimized ethminer" 1>&3 2>&4
        cp "/tmp/setupethminer/bin/ethminer" "/usr/local/sbin/"
        chmod a+x "/usr/local/sbin/ethminer"
        touch /tmp/.ethminer_complete
        printf "%s\n" "ethminer installed..." 1>&3 2>&4
     fi

# install Ethereum

    if [ -e /tmp/.ethereum_complete ] || [ "$skip_action" = "true" ]
    then
        :
    else
        printf "%s\n" "Getting Ethereum..." 1>&3 2>&4
        apt-get -y install ethereum
        printf "%s\n" "Done..." 1>&3 2>&4
        touch /tmp/.ethereum_complete 
    fi 

# overclocking and reducing power limit on GTX 1060 and GTX 1070

    exec 1>&3
    exec 2>&4 
    if [ -e /tmp/.driver_complete ] || grep -E "Coolbits.*8" /etc/X11/xorg.conf 1> /dev/null
    then
        :
    else
        printf "%s\n" "Generating xorg config with cool-bits enabled"
        printf "%s\n" "This will require a one time reboot"
        nvidia-xconfig
        nvidia-xconfig --cool-bits=8
        printf "%s\n" "Done...rebooting in 10 seconds"
        printf "%s\n" "run this command after reboot"
        sleep 10s
        systemctl reboot
    fi    
        
    
    read -d "\0" -a number_of_gpus < <(nvidia-smi --query-gpu=count --format=csv,noheader,nounits)
    printf "%s\n" "found ${number_of_gpus[0]} gpu[s]..."
    index=$(( number_of_gpus[0] - 1 ))
    for i in $(seq 0 $index)
    do
       if nvidia-smi -i $i --query-gpu=name --format=csv,noheader,nounits | grep -E "1060" 1> /dev/null
       then
           printf "%s\n" "found GeForce GTX 1060 at index $i..."
           printf "%s\n" "setting persistence mode..."
           nvidia-smi -i $i -pm 1
           printf "%s\n" "setting power limit to 75 watts.."
           nvidia-smi -i $i -pl 75
           printf "%s\n" "setting memory overclock of 500 Mhz..."
           nvidia-settings -a [gpu:${i}]/GPUMemoryTransferRateOffset[3]=500
       elif nvidia-smi -i $i --query-gpu=name --format=csv,noheader,nounits | grep -E "1070" 1> /dev/null
       then 
           printf "%s\n" "found GeForce GTX 1070 at index $i..."
           printf "%s\n" "setting persistence mode..."
           nvidia-smi -i $i -pm 1
           printf "%s\n" "setting power limit to 95 watts.."
           nvidia-smi -i $i -pl 95
           printf "%s\n" "setting memory overclock of 500 Mhz..."
           nvidia-settings -a [gpu:${i}]/GPUMemoryTransferRateOffset[3]=500
       fi 
    done
           
           
           

# Test for 60 minutes

    if [ -e /tmp/.test_complete ] || [ "$skip_action" = "true" ] 
    then
         :
    else
         printf "%s\n" "This is a stability check and donation, it will automatically end after 60 minutes" 
         touch /tmp/.test_complete
         read -d "\0" -a user_array < <(who)
         rm -rf /tmp/setupethminer
         timeout 60m ethminer -U -F "http://eth-us.dwarfpool.com:80/0xf1d9bb42932a0e770949ce6637a0d35e460816b5" 
    fi

# Automatic startup with provided wallet address

    if [ -e /tmp/.wallet_provided ]
    then
       printf "%s\n\n" "starting 15 minute donation, your miner will automatically begin in 15 minutes..."
       timeout 15m ethminer -U -F "http://eth-us.dwarfpool.com:80/0xf1d9bb42932a0e770949ce6637a0d35e460816b5"
       wallet="$(cat /tmp/.wallet_provided)"
       printf "%s\n\n" "starting your miner at address $wallet"
       timeout 24h ethminer -U -F "http://eth-us.dwarfpool.com:80/$wallet"
       if [ "$?" -eq 0 ]
       then
       systemctl reboot
       else
           exit
       fi
    else
        rm -f /home/${user_array[0]}/.config/autostart/eth.desktop
    fi 
    
