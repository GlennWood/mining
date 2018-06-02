#!/bin/bash

###
### To create bootable USB from currently running Ubuntu.
### Ref: https://answers.launchpad.net/systemback/+question/273061#5

cat << HELP

When the systemback window appears on your X-server client,

  1. Log into systemback as '$MINERS_USER'.
  2. Click "Live system create".
  3. Click "Create new".
     - this will take about eight (8) minutes.
  4. Select the image under "Created Live images".
  5. Click "Convert to ISO" (if you want an ISO).
     - this will take just a minute or two.
  6. Exit by hovering over upper-right-corner and then click "X"
  7. After systemback exits, return to this ssh session for further instructions.

You will then have a live system backup and an ISO in /home/systemback_live_<TODAYS_DATE>.{sblive,iso}

As a security feature, before systemback is started your .bash_history files will be truncated.

HELP
read -p "Hit Enter when you are ready to proceed." PROCEED
sudo truncate -s 0 /home/$MINERS_USER/.bash_history /root/.bash_history
/usr/lib/systemback/sbsustart systemback
SBLIVE_DATE=`date +%Y-%m-%d`
ll /home/systemback_live_${SBLIVE_DATE}*
echo 'Your sblive backup is complete.'
