#!/usr/bin/python
"""Usage: miners.py OPERATION [-fhX] [--platform typ] [--force] [--dryrun] [MINERS] ...

Apply OPERATION to the mining of designated COINs w

Arguments:
  OPERATION  install | status
               (a comma-separated list of OPERATIONs)
  MINERS     comma-seperated list of miners to (re)install

Options:
  --platform typ  AMD, NVI, BTH [default: BTH]
  -f --force   force execution, ignoring non-critical warnings
  -h --help
  -v           verbose mode
  -q --quick   quick mode
  -X --dryrun  print the command that would execute, then exit
"""

from __future__ import print_function
import os
import sys
sys.path.insert(0,'/opt/mining/mining')

from MinersInstaller import MinersInstaller
from docopt import docopt
import config

MINERS_INSTALLERS = {
'CGMINER': [ 'cgminer',
      'wget http://ck.kolivas.org/apps/cgminer/4.9/cgminer-4.9.2.tar.lrz',
      ['build-essential', 'autoconf', 'automake', 'libtool', 'pkg-config', 'libcurl3-dev', 'libudev-dev', 'libcurl4-openssl-dev'],
      ['cd cgminer-4.9.2', 'CFLAGS="-O2 -Wall -march=native" ./configure', 'make', 'make install']
    ],
'TPROVOT': [ 'tpruvot',
      'https://github.com/tpruvot/ccminer.git',
      ['automake pkg-config', 'libtool', 'libcurl4-openssl-dev', 'libssl-dev', 'libjansson-dev', 'automake', 'autotools-dev', 'build-essential'],
      ['cd ccminer', './autogen.sh', './configure', './build.sh']
    ],
'KLAUST': [ 'ccminer-KlausT',
      'https://github.com/KlausT/ccminer.git ccminer-KlausT',
      ['automake', 'autotools-dev', 'pkg-config', 'libtool', 'libcurl4-openssl-dev', 'libjansson-dev',
        'libssl-dev', 'libcurl4-openssl-dev', 'libssl-dev', 'libjansson-dev', 'build-essential', 'CUDA-9'],
      ['cd ccminer-KlausT', 'git checkout cuda9', './autogen.sh', './configure',
       "sed -i.bak 's/SHFL[(]/SHFL_UP(/g' bitslice_transformations_quad.cu groestl_functions_quad.cu lyra2/cuda_lyra2v2.cu x11/cuda_x11_simd512.cu neoscrypt/cuda_neoscrypt_tpruvot.cu",
       './build.sh', './ccminer --ndevs']
    ],
'GATELESSGATE': [ 'gatelessgate',
      'https://github.com/zawawawa/gatelessgate.git',
      ['libcurl4-openssl', 'dev pkg-config', 'libtool', 'libncurses5-dev'],
      ['cd ccminer-KlausT', 'git submodule init', 'git submodule update', 'cd Core', 'autoreconf -i', 'CFLAGS="-O2 -Wall -march=native -std=gnu99 -ggdb" ./configure --without-curses',
       'make', '.make install', 'gatelessgate --version']
    ],
'suprminer': [ 'suprminer',
      'https://github.com/ocminer/suprminer.git',
      ['automake','autotools-dev','pkg-config','libtool','libcurl4-openssl-dev','libjansson-dev'],
      ['./autogen.sh', './configure', './build.sh', './ccminer --ndevs']
    ],
'avermore-miner': [ 'avermore-miner',
      'https://github.com/brian112358/avermore-miner.git',
      ['libcurl4-openssl-dev', 'pkg-config', 'libtool', 'libncurses5-dev'],
      ['git submodule init', 'git submodule update', 'autoreconf -i', 'CFLAGS="-O2 -Wall -march=native -std=gnu99" ./configure --without-curses',
       'make', '[ -f /usr/local/bin/sgminer ] && mv /usr/local/bin/sgminer /usr/local/bin/sgminer-save',
       'make install', 'mv /usr/local/bin/sgminer /usr/local/bin/sgminer-gm-x16r',
       '[ -f /usr/local/bin/sgminer-save ] && mv /usr/local/bin/sgminer-save /usr/local/bin/sgminer']
    ],
'nevermore-miner': [ 'nevermore-miner',
      'https://github.com/brian112358/nevermore-miner.git',
      ['libcurl4-openssl-dev', 'pkg-config', 'libtool', 'libncurses5-dev'],
      ['git submodule init', 'git submodule update', 'autoreconf -i', 'CFLAGS="-O2 -Wall -march=native -std=gnu99" ./configure --without-curses',
       'make', '[ -f /usr/local/bin/sgminer ] && mv /usr/local/bin/sgminer /usr/local/bin/sgminer-save',
       'make install', 'mv /usr/local/bin/sgminer /usr/local/bin/sgminer-gm-x16r',
       '[ -f /usr/local/bin/sgminer-save ] && mv /usr/local/bin/sgminer-save /usr/local/bin/sgminer']
    ],
'SGMINER': [ 'sgminer',
      'https://github.com/nicehash/sgminer.git',
      ['libcurl4-openssl-dev', 'pkg-config', 'libtool', 'libncurses5-dev'],
      ['cd sgminer', 'git submodule init', 'git submodule update', 'autoreconf -i', 'CFLAGS="-O2 -Wall -march=native -std=gnu99" ./configure --without-curses',
       "sed -i.bak 's/pool->backup = TRUE;/pool->backup = true;/' sgminer.c",
       'make', '.make install', 'sgminer --version']
    ],
'sgminer-gm-x16r': [ 'sgminer-gm-x16r',
      'https://github.com/aceneun/sgminer-gm-x16r.git',
      ['libcurl4-openssl-dev', 'pkg-config', 'libtool', 'libncurses5-dev'],
      ['cd sgminer-gm-x16r', 'git submodule init', 'git submodule update', 'autoreconf -i', 'CFLAGS="-O2 -Wall -march=native -std=gnu99" ./configure --without-curses',
       'make', '[ -f /usr/local/bin/sgminer ] && mv /usr/local/bin/sgminer /usr/local/bin/sgminer-save',
       '.make install', 'mv /usr/local/bin/sgminer /usr/local/bin/sgminer-gm-x16r'
        '[ -f /usr/local/bin/sgminer-save ] && mv /usr/local/bin/sgminer-save /usr/local/bin/sgminer',
        'sgminer --version']
    ],
'xmr-stak': [ 'xmr-stak',
      'https://github.com/fireice-uk/xmr-stak.git',
      ['libmicrohttpd-dev', 'libssl-dev', 'cmake', 'build-essential', 'libhwloc-dev'],
      ['mkdir /opt/xmr-stak/build', 'cd /opt/xmr-stak/build', 'cmake .. -DCMAKE_LINK_STATIC=ON -DOpenCL_ENABLE=OFF -DCUDA_ARCH=30', 
       'make install', 'ln -sf /opt/xmr-stak/build/bin/xmr-stak /usr/local/bin/xmr-stak', 'xmr-stak --version;true']
    ],
}


################################################################################################
def bash_completion(config):
    for idx in xrange(len(sys.argv)-1,0,-1):
        cur = sys.argv[idx]
        print(cur.upper())
        if cur in {'install':1,'status':1}:
            print('ALL '+' '.join(MINERS_INSTALLERS.keys()))
            sys.exit(0)
        print('install status')

################################################################################################
config = config.Config(docopt(__doc__, argv=None, help=True, version=None, options_first=False))

if not config.arguments['OPERATION'] or config.arguments['OPERATION'] not in {'install':1,'status':1,'bash_completion':1}:
    print("USAGE: "+sys.argv[0]+" [ install | status ] [ miner-name ... ]")
    sys.exit(1)
if config.arguments['OPERATION'] == 'bash_completion':
    bash_completion(config)
    sys.exit(0)

if 'ALL' in config.arguments['MINERS']:
    config.arguments['MINERS'] = MINERS_INSTALLERS.keys()

if config.arguments['OPERATION'] == 'install':
    for miner in config.arguments['MINERS']:
        # TODO verify 'miner' is in MINERS_INSTALLERS
        MinersInstaller(MINERS_INSTALLERS[miner])
    os.chdir('/opt')
    MinersInstaller.install_all(config)
    print("All done!")
elif config.arguments['OPERATION'] == 'status':
    print ("'install_miners status' is not yet implemented.")


'''

CUDA_CFLAGS="--gpu-architecture=compute_50 --gpu-code=sm_50,compute_50" 

suprminer Makefile.am
...
nvcc_ARCH :=
nvcc_ARCH += -gencode=arch=compute_61,code=\"sm_61,compute_61\"
nvcc_ARCH += -gencode=arch=compute_52,code=\"sm_52,compute_52\"
nvcc_ARCH += -gencode=arch=compute_50,code=\"sm_50,compute_50\"
#nvcc_ARCH += -gencode=arch=compute_35,code=\"sm_35,compute_35\"
#nvcc_ARCH += -gencode=arch=compute_30,code=\"sm_30,compute_30\"
...
'''

'''
export CC=/usr/bin/gcc-6
export CXX=/usr/bin/g++-6
cmake -DCMAKE_LINK_STATIC=ON -DXMR-STAK_COMPILE=generic -DCUDA_ENABLE=ON -DOpenCL_ENABLE=OFF -DMICROHTTPD_ENABLE=ON
make -j 12
make install

'''
