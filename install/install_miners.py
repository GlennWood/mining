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
