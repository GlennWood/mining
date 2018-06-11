#!/usr/bin/python3
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
import sys
### Ref: http://python-future.org/compatible_idioms.html
from builtins import range

from MinersInstaller import MinersInstaller
from docopt import docopt
import yaml

RC = 0
MINERS_INSTALLERS = {}
with open("/opt/mining/install/installers.yml", 'r') as stream:
    try:
        MINERS_INSTALLERS = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        sys.exit(1)


################################################################################################
def bash_completion(config):
    for idx in range(len(sys.argv)-1,0,-1):
        cur = sys.argv[idx]
        if cur in {'install':1,'status':1}:
            print('ALL '+' '.join(MINERS_INSTALLERS.keys()))
            sys.exit(0)
        print('install status')

################################################################################################
arguments = docopt(__doc__, argv=None, help=True, version=None, options_first=False)

if not arguments['OPERATION'] or arguments['OPERATION'] not in {'install':1,'status':1,'bash_completion':1}:
    print("USAGE: "+sys.argv[0]+" [ install | status ] [ miner-name ... ]")
    sys.exit(1)
if arguments['OPERATION'] == 'bash_completion':
    bash_completion(arguments)
    sys.exit(RC)

if 'ALL' in arguments['MINERS']:
    arguments['MINERS'] = MINERS_INSTALLERS.keys()

if arguments['OPERATION'] == 'install':
    for miner in arguments['MINERS']:
        # TODO verify 'miner' is in MINERS_INSTALLERS
        if miner in MINERS_INSTALLERS:
            MinersInstaller(MINERS_INSTALLERS[miner])
        else:
            print("'"+miner+"' is not configured in InstallMiners.py",file=sys.stderr)
            RC = 1
    if RC is 0:
        MinersInstaller.install_all(arguments)
        if not arguments['--dryrun']: print("All done!")
elif arguments['OPERATION'] == 'status':
    print("'install_miners status' is not yet implemented.")

sys.exit(RC)
