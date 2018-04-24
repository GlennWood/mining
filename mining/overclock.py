import os
import sys

'''
root@rig-19X:~# nvidia-smi -L
GPU 0: GeForce GTX 1070 Ti (UUID: GPU-fb93da66-2fe6-d559-1673-e28d72cc996f)
GPU 1: GeForce GTX 1070 Ti (UUID: GPU-189cf176-3185-2880-f049-594754bbcd16)
GPU 2: GeForce GTX 1070 Ti (UUID: GPU-07f46ba7-8727-c538-373d-81e81db6d1e6)
GPU 3: GeForce GTX 1070 (UUID: GPU-3fbd9994-bdfc-dc17-45ec-e691f3ad4a17)
GPU 4: GeForce GTX 1070 (UUID: GPU-b9e933d0-5c48-19d3-2765-64cd8f54b7db)
GPU 5: GeForce GTX 1070 (UUID: GPU-3e321474-214c-c305-a479-255a616c8e35)
GPU 6: GeForce GTX 1070 Ti (UUID: GPU-292fec7a-5f82-2a5c-480c-24f60d1a8316)
GPU 7: GeForce GTX 1070 (UUID: GPU-22d50ff2-2ae8-6e7f-b9fb-e6be717fa79b)
'''


def process(self, config, coin):
    if config.VERBOSE: print(__name__+".process("+coin['COIN']+")")

    cmd = 'overclock module is NYI'
    try:
        if config.VERBOSE: print cmd
        # Fork this!
        newpid = os.fork()
        if newpid == 0: return 0

        try: os.setsid()
        except OSError as ex:# 'fork of './ccminer' failed: 1 (Operation not permitted)' 
            newpid = newpid#  due to python's exception when you are already the group-leader ... 
        os.umask(0)
             
        os.system(cmd)

    except SystemExit as ex:
        print "Exiting"
    except OSError as ex:
        print >> sys.stderr, "fork failed: %d (%s)" % (ex.errno, ex.strerror)
        sys.exit(1)
    except:
        ex = sys.exc_info()[0]
        print ( ex )


def initialize(self, config, coin):
    if config.VERBOSE: print(__name__+".initialize("+coin['COIN']+")")
    return 0

def finalize(self, config, coin):
    if config.VERBOSE: print(__name__+".finalize("+coin['COIN']+")")
    return 0
