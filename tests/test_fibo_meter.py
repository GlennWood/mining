#!/usr/bin/python
import sys
sys.path.insert(0,'/opt/mining/mining')
sys.path.insert(0,'/opt/mining/monitor')
from fibo_meter import FiboMeter

fiboMeter = FiboMeter(1,2,2)

for idx in xrange(44):
    if fiboMeter.next():
        print str(idx)+" True"
    else:
        print str(idx)+" False"
