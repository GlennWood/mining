#!/usr/bin/python3

from __future__ import print_function
import sys
### Ref: http://python-future.org/compatible_idioms.html
from builtins import range

MINERS_INSTALLERS = {
'bminer': [ 'bminer', None, None, 'install-bminer' ],
'avermore-miner': [ 'avermore-miner',
      'https://github.com/brian112358/avermore-miner.git',
      ['libcurl4-openssl-dev', 'pkg-config', 'libtool', 'libncurses5-dev'],
      ['git submodule init', 'git submodule update', 'autoreconf -i', 'CFLAGS="-O2 -Wall -march=native -std=gnu99" ./configure --without-curses',
       'make', '[ -f /usr/local/bin/sgminer ] && mv /usr/local/bin/sgminer /usr/local/bin/sgminer-save',
       'make install', 'mv /usr/local/bin/sgminer /usr/local/bin/sgminer-gm-x16r',
       '[ -f /usr/local/bin/sgminer-save ] && mv /usr/local/bin/sgminer-save /usr/local/bin/sgminer']
    ],
'cgminer': [ 'cgminer',
      'wget http://ck.kolivas.org/apps/cgminer/4.9/cgminer-4.9.2.tar.lrz',
      ['build-essential', 'autoconf', 'automake', 'libtool', 'pkg-config', 'libcurl3-dev', 'libudev-dev', 'libcurl4-openssl-dev'],
      ['cd cgminer-4.9.2', 'CFLAGS="-O2 -Wall -march=native" ./configure', 'make', 'make install']
    ],
'claymore-neoscrypt': [ 'claymore-neoscrypt', None, None, 'install-claymore-neoscrypt' ],
'dstm': [ 'dstm', None, None, 'install-dstm' ],
'klaust': [ 'ccminer-KlausT',
      'https://github.com/KlausT/ccminer.git ccminer-KlausT',
      ['automake', 'autotools-dev', 'pkg-config', 'libtool', 'libcurl4-openssl-dev', 'libjansson-dev',
        'libssl-dev', 'libcurl4-openssl-dev', 'libssl-dev', 'libjansson-dev', 'build-essential', 'CUDA-9'],
      ['cd ccminer-KlausT', 'git checkout cuda9', './autogen.sh', './configure',
       "sed -i.bak 's/SHFL[(]/SHFL_UP(/g' bitslice_transformations_quad.cu groestl_functions_quad.cu lyra2/cuda_lyra2v2.cu x11/cuda_x11_simd512.cu neoscrypt/cuda_neoscrypt_tpruvot.cu",
       './build.sh', './ccminer --ndevs']
    ],
'gatelessgate': [ 'gatelessgate',
      'https://github.com/zawawawa/gatelessgate.git',
      ['libcurl4-openssl', 'dev pkg-config', 'libtool', 'libncurses5-dev'],
      ['cd ccminer-KlausT', 'git submodule init', 'git submodule update', 'cd Core', 'autoreconf -i', 'CFLAGS="-O2 -Wall -march=native -std=gnu99 -ggdb" ./configure --without-curses',
       'make', '.make install', 'gatelessgate --version']
    ],
'ethdcrminer64': [ 'ethdcrminer64', None, None, 'install-ethdcrminer64' ],
'ethminer': [ 'ethminer', None, None, 'install-ethminer' ],
'ewbf': [ 'ewbf', None, None, 'install-ewbf' ],
'ngsminer': [ 'ngsminer', None, None, 'install-ngsminer' ],
'nheqminer': [ 'nheqminer', None, None, 'install-nheqminer' ],
'nevermore-miner': [ 'nevermore-miner',
      'https://github.com/brian112358/nevermore-miner.git',
      ['libcurl4-openssl-dev', 'pkg-config', 'libtool', 'libncurses5-dev'],
      ['git submodule init', 'git submodule update', 'autoreconf -i', 'CFLAGS="-O2 -Wall -march=native -std=gnu99" ./configure --without-curses',
       'make', '[ -f /usr/local/bin/sgminer ] && mv /usr/local/bin/sgminer /usr/local/bin/sgminer-save',
       'make install', 'mv /usr/local/bin/sgminer /usr/local/bin/sgminer-gm-x16r',
       '[ -f /usr/local/bin/sgminer-save ] && mv /usr/local/bin/sgminer-save /usr/local/bin/sgminer']
    ],
'optiminer-equihash': [ 'optiminer-equihash', None, None, 'install-optiminer-equihash' ],
'optiminer-zcash': [ 'optiminer-zcash', None, None, 'install-optiminer-zcash' ],
'sgminer': [ 'sgminer',
      'https://github.com/nicehash/sgminer.git',
      ['libcurl4-openssl-dev', 'pkg-config', 'libtool', 'libncurses5-dev'],
      ['cd sgminer', 'git submodule init', 'git submodule update', 'autoreconf -i', 'CFLAGS="-O2 -Wall -march=native -std=gnu99" ./configure --without-curses',
       "sed -i.bak 's/pool->backup = TRUE;/pool->backup = true;/' sgminer.c",
       'make', '.make install', 'sgminer --version']
    ],
'sgminer-dev': [ 'sgminer-dev', None, None, 'install-sgminer-dev' ],
'sgminer-phi': [ 'sgminer-phi', None, None, 'install-sgminer-phi' ],
'sgminer-gm-x16r': [ 'sgminer-gm-x16r',
      'https://github.com/aceneun/sgminer-gm-x16r.git',
      ['libcurl4-openssl-dev', 'pkg-config', 'libtool', 'libncurses5-dev'],
      ['cd sgminer-gm-x16r', 'git submodule init', 'git submodule update', 'autoreconf -i', 'CFLAGS="-O2 -Wall -march=native -std=gnu99" ./configure --without-curses',
       'make', '[ -f /usr/local/bin/sgminer ] && mv /usr/local/bin/sgminer /usr/local/bin/sgminer-save',
       '.make install', 'mv /usr/local/bin/sgminer /usr/local/bin/sgminer-gm-x16r'
        '[ -f /usr/local/bin/sgminer-save ] && mv /usr/local/bin/sgminer-save /usr/local/bin/sgminer',
        'sgminer --version']
    ],
'suprminer': [ 'suprminer',
      'https://github.com/ocminer/suprminer.git',
      ['automake','autotools-dev','pkg-config','libtool','libcurl4-openssl-dev','libjansson-dev'],
      ['./autogen.sh', './configure', './build.sh', './ccminer --ndevs']
    ],
'tpruvot': [ 'tpruvot',
      'https://github.com/tpruvot/ccminer.git',
      ['automake pkg-config', 'libtool', 'libcurl4-openssl-dev', 'libssl-dev', 'libjansson-dev', 'automake', 'autotools-dev', 'build-essential'],
      ['./autogen.sh', './configure', './build.sh']
    ],
'xmr-stak': [ 'xmr-stak',
      'https://github.com/fireice-uk/xmr-stak.git',
      ['libmicrohttpd-dev', 'libssl-dev', 'cmake', 'build-essential', 'libhwloc-dev'],
      ['mkdir /opt/xmr-stak/build', 'cd /opt/xmr-stak/build', 'cmake .. -DCMAKE_LINK_STATIC=ON -DOpenCL_ENABLE=OFF -DCUDA_ARCH=30', 
       'make install', 'ln -sf /opt/xmr-stak/build/bin/xmr-stak /usr/local/bin/xmr-stak', 'xmr-stak --version;true']
    ],
'zecminer64': [ 'zecminer64', None, None, 'install-zecminer64' ],
}


################################################################################################
import config
config = config.Config(None)

################################################################################################
for idx in range(len(sys.argv)-1,0,-1):
    cur = sys.argv[idx]
    if cur in {'install':1,'status':1}:
        print('ALL '+' '.join(MINERS_INSTALLERS.keys()))
    else:
        print('install status')
