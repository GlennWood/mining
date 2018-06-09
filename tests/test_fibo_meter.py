#!/usr/bin/python
from __future__ import print_function
import sys
sys.path.insert(0,'/opt/mining/mining')
sys.path.insert(0,'/opt/mining/monitor')
from fibo_meter import FiboMeter
### Ref: http://python-future.org/compatible_idioms.html
from builtins import range

fiboMeter = FiboMeter(1,2,2)

for idx in range(44):
    if fiboMeter.next():
        print(str(idx)+" True")
    else:
        print(str(idx)+" False")
