#!/usr/bin/python
"""Usage: miners.py OPERATION [-fhX] [--platform typ] [--force] [--dryrun] [MINERS] ...

Apply OPERATION to the mining of designated COINs w

Arguments:
  OPERATION  install
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
'ccminer': [ 'ccminer',
      'https://github.com/tpruvot/ccminer.git',
      ['automake pkg-config', 'libtool', 'libcurl4-openssl-dev', 'libssl-dev', 'libjansson-dev', 'automake', 'autotools-dev', 'build-essential'],
      ['cd ccminer', './autogen.sh', './configure', './build.sh']
    ],
    'suprminer': [ 'suprminer',
      'https://github.com/ocminer/suprminer.git',
      ['automake','autotools-dev','pkg-config','libtool','libcurl4-openssl-dev','libjansson-dev'],
      ['./autogen.sh', './configure', './build.sh', './ccminer --ndevs']
    ],
    'xmr-stak': [ 'xmr-stak',
      'https://github.com/fireice-uk/xmr-stak.git',
      ['libmicrohttpd-dev', 'libssl-dev', 'cmake', 'build-essential', 'libhwloc-dev'],
      ['mkdir /opt/xmr-stak/build', 'cd /opt/xmr-stak/build', 'cmake .. -DCMAKE_LINK_STATIC=ON -DOpenCL_ENABLE=OFF -DCUDA_ARCH=30', 'make install', 'ln -sf /opt/xmr-stak/build/bin/xmr-stak /usr/local/bin/xmr-stak', 'xmr-stak --version;true']
    ]
}

config = config.Config(docopt(__doc__, argv=None, help=True, version=None, options_first=False))
if not config.arguments['MINERS']:
    config.arguments['MINERS'] = MINERS_INSTALLERS.keys()

for miner in config.arguments['MINERS']:
    MinersInstaller(MINERS_INSTALLERS[miner])

os.chdir('/opt')
MinersInstaller.install_all(config)
print("All done!")
