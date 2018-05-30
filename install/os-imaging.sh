#/bin/bash

### NOW CLONE THIS SO WE DON'T HAVE TO DO THIS OVER AND OVER AANNDOVER OASCO OVER AND OVER AND OVER!!!!!!!
### https://www.makeuseof.com/tag/2-methods-to-clone-your-linux-hard-drive/

echo 'This will take about eight (8) minutes'
dd if=/dev/sda of=/dev/sdb bs=64K conv=noerror,sync
