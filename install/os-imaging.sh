#/bin/bash

    if [[ $EUID -ne 0 ]]
    then
		echo "$0 must be run as root."
		sudo -H $0 $*
		exit $?
	fi

### Ref: http://releases.ubuntu.com/16.04/
###      http://releases.ubuntu.com/16.04/ubuntu-16.04.4-server-i386.iso
### Ref: http://releases.ubuntu.com/18.04/
###      

###
### To create bootable USB from currently running Ubuntu.
### Ref: https://answers.launchpad.net/systemback/+question/273061#5
=============================================== systemback
### Generate sblive image of currently running Ubuntu.
add-apt-repository -y ppa:nemh/systemback
apt-get update
apt-get -y install systemback unionfs-fuse genisoimage

# AS USER $MINERS_USER
sudo systemback

# To generate the ISO file:

1. Decompress the .sblive image:
mkdir sblive
tar -xf /home/{ the-name-you-gave-it}.sblive -C sblive

2. Rename the syslinux to isolinux:
mv sblive/syslinux/syslinux.cfg sblive/syslinux/isolinux.cfg
mv sblive/syslinux sblive/isolinux

3. Generate the ISO file:
genisoimage -iso-level 3 -r -V sblive -cache-inodes -J -l -b isolinux/isolinux.bin -no-emul-boot -boot-load-size 4 -boot-info-table -c isolinux/boot.cat -o mining-20180520.iso sblive

add-apt-repository -y ppa:gezakovacs/ppa
apt-get update ; apt-get -y install unetbootin

## mount -t vfat /dev/sda2 /media/usb -o uid=1000,gid=100,utf8,dmask=027,fmask=137
## mount -t ntfs-3g /dev/sda2 /media/usb
## neither of those worked, so I just copied the ISO to my MacBook and ran Unetbootin from there.



### CLONING AN SSD SO WE DON'T HAVE TO DO THIS OVER AND OVER AANNDOVER OASCO OVER AND OVER AND OVER!!!!!!!
### https://www.makeuseof.com/tag/2-methods-to-clone-your-linux-hard-drive/

echo 'This will take about eight (8) minutes'
dd if=/dev/sda of=/dev/sdb bs=64K conv=noerror,sync


### OR
add-apt-repository -y ppa:nemh/systemback
apt-get update
apt-get -y install systemback unionfs-fuse

# AS USER $MINERS_USER
sudo systemback


### Ref: https://help.ubuntu.com/community/mkusb
### 'mkusb - dd image of iso file to USB device safely'
add-apt-repository -y universe
add-apt-repository -y ppa:mkusb/ppa
apt-get update
apt-get -y install mkusb mkusb-nox usb-pack-efi

### Ref: http://phillw.net/isos/linux-tools/mkusb/mkUSB-quick-start-manual.pdf
mkusb /home/miners-2018-05-22.iso


### Clean up logs
cd $MINING_ROOT/install/log
sudo su
> lastlog
> wtmp
> dpkg.log 
> kern.log
> syslog
exit

