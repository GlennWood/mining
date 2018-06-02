Backing up your entire system
==============================
TODO: a more useful README here.
Make backup with Systemback
---------------------------

    systemback
When the systemback window appears on your X-server client,

  1. Log into systemback as your '$MINERS_USER'.
  2. Click "Live system create".
  3. Click "Create new".
     - this will take about eight (8) minutes.
  4. Select the image under "Created Live images".
  5. Click "Convert to ISO" (if you want an ISO).
     - this will take just a minute or two.
  6. Exit by hovering over upper-right-corner and then click "X"

You will then have a live system backup and an ISO in /home/systemback_live_<TODAYS_DATE>.{sblive,iso}

As a security feature, before *systemback* is started your .bash_history files will be truncated.

Restore system from Systemback's Live Image
-----------------------------------

You may now use the sblive image to restore this system to a new drive.

  1. Plug in a target drive (USB or SSD)
  2. Enter `systemback`
  3. Log into *systemback* as '$MINERS_USER'.
  4. Click 'System install'.
  5. Enter user account, password(s) and hostname; click 'Next'
  6. Now here is where it gets a little complicated
     - there are a couple of tasks you would never do elsewhere
     - the UX is a bit non-intuitive
  7. You should see something like '/dev/sda' and '/dev/sdb'
     - one is your running system, the other the target for your new install.
     - the target is likely mounted on /media/$MINING_USER
     - the shell command 'df' can help you figure out which is which
  8. Pick the one to which you want to install.
  9. Click "Unmount" (if offered).
  10. Click "! Delete !".
  11. Create partitions in '/dev/sdb?' or '/dev/sba?', as appropriate.
     - Click '/dev/sdb?' or '/dev/sba?', as appropriate.
     - Enter '512 MiB' under 'Create new'.
     - Click the left-arrow on the mid-right-hand panel.
  12. Repeat #11 for two more partitions:
     - '2 GiB'
     - all the rest in a final partition
  13. Mount the '512 MiB' partition to '/boot/efi'
     - Click on the '512 MiB' partition in the left panel
     - Select '/boot/efi' from the 'Mount point' dropdown.
     - Click the left-arrow on the mid-right-hand panel.
  14. Repeat #13 for
     - mount 'SWAP' to the '2 GiB' partition.
     - mount '/' to the remaining partition.
  15. Click the 'Next' button.

You will now have a new system installed on your selected device.
