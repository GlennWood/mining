from __future__ import print_function
import xlrd
import re
import os
import sys
import jprops

class Config(object):

    MINERS_XLSX = '/opt/mining/miners.xlsx'
    ALL_MEANS_ONCE = -11111
    I_AM_FORK = False
    RC_MAIN = 0

    SHEETS = {
        'Globals': None,
        'CoinMiners': None,
        'Clients': None,
        'WhatToMine': None,
        'Overclock': None
        }
    
    def __init__(self, argumentsIn):
        self.arguments = argumentsIn

        # Global Variables
        self.PLAT_COINS = {'AMD': {}, 'NVI': {}, 'BTH': {}}
        self.WORKER_NAME = ''
        self.StatsUrls = {}
        self.ConvertUrls = {}
    
        # Command line options, values
        self.OPS = self.arguments['OPERATION'].split(',')
        if '--platform' in self.arguments:
            self.PLATFORM = self.arguments['--platform']
        else:
            self.PLATFORM = os.getenv('PLATFORM','BTH')
        if '--url-port' in self.arguments: self.URL_PORT = self.arguments['--url-port']
        self.ALL_COINS = self.arguments['COIN'] is None or len(self.arguments['COIN']) == 0

        # Command line options, booleans
        self.URL_PORT = self.SCOPE = None
        self.VERBOSE  = self.arguments['-v']
        self.PRINT    = self.arguments['--print']
        self.DRYRUN   = self.arguments['--dryrun']
        self.QUICK    = self.arguments['--quick']
        self.SCOPE    = self.arguments['--scope']
        self.WIDE_OUT = self.arguments['-l']
        self.FORCE    = self.arguments['--force']
     
        self.setup_config_dicts()
        self.setup_ansible_config()
        return
  

    # Parse sheets from miners.xslx
    def setup_config_dicts(self):

        # Put Stats sheet into stats_dict
        workbook = xlrd.open_workbook(self.MINERS_XLSX)
        for sheet_name in workbook.sheet_names():
            sheet = workbook.sheet_by_name(sheet_name)
            self.SHEETS[sheet_name] = {}
            keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
            prev_key = None
            for row_index in xrange(1, sheet.nrows):
                row = {keys[col_index]: sheet.cell(row_index, col_index).value 
                    for col_index in xrange(sheet.ncols)}

                if sheet_name == 'CoinMiners': # CoinMiners' sheet is handled differently
                    row, prev_key = self.setup_CoinMiners_dict(row, prev_key)
                elif sheet_name == 'WhatToMine': # WhatToMine is keyed by column, not row
                    self.SHEETS[sheet_name] = self.pivot_sheet(self.SHEETS[sheet_name], row, keys)
                else:
                    key = row[keys[0]]
                    if key:
                        self.SHEETS[sheet_name][key.upper()] = row

        if self.ALL_COINS: 
            self.arguments['COIN'] = [x.upper() for x in sorted(list(self.SHEETS['CoinMiners'].keys()))]   

        return [self.SHEETS['Stats'],self.StatsUrls,self.ConvertUrls,self.SHEETS['CoinMiners'],self.SHEETS['Clients']]

    '''
    The miners.xslx/WhatToMine spreadsheet is mapped from the keys on the first
    row into the columns under each key, so we do that way here rather than the 
    default of first-column => columns (as above).
    '''
    def pivot_sheet(self, sheet, row, keys):
        for key in keys:
            if key == 'Param':
                param = row[key]
            else:
                row_val = row[key]
                if key not in sheet:
                    sheet[key] = { }
                sheet[key][param] = row_val
        return sheet


    #
    # The CoinMiners sheet enables a number of special configurable configurating.
    #   1. The OPTIONS field is configured on a line following the main config (to give more room to spell out the OPTIONS)
    #   2. The MINER can be specified as a key to the Clients spreadsheet to spell out the CoinMiner's options
    #   2a. (this MNEMONICS capability is actually facilitated in the start option-module)
    #
    def setup_CoinMiners_dict(self, row, prev_key):
        if prev_key is None and row['COIN'].strip():
            prev_key = row['COIN'].upper()
        # The CoinMiners sheet has a special way of enabling a wider OPTIONS cell
        row['OPTIONS']='' # There is no OPTIONS column native to the CoinMiners sheet
        if not row['COIN'].strip():
            self.SHEETS['CoinMiners'][prev_key]['OPTIONS'] = row['MINER']
            return row, prev_key
        # Apply the '--url-port' command-line option, if exists.
        if self.URL_PORT:
            row['URL_PORT'] = self.URL_PORT
        # Provision $URL and $PORT as alternatives to $URL_PORT
        regex = re.compile(r'(.*)[:]([0-9]{4,5})', re.DOTALL)
        match = regex.match(row['URL_PORT'])
        if match != None:
            row['URL'] = match.group(1)
            row['PORT'] = match.group(2)
        # Replace $USER_PSW, and/or $USER and $PSW, with configured value(s)
        USER_PSW = row['USER_PSW'].split(':')
        if len(USER_PSW) > 1:
            row['USER'] = USER_PSW[0]
            row['PASSWORD'] = USER_PSW[1]
        else:
            row['USER'] = row['USER_PSW']
            row['PASSWORD'] = '' #None

        prev_key = row['COIN'].upper()

        #if prev_key: 
        # Index each coinMiner under the applicable platform, AMD, NVI or BTH
        plat = row['PLAT']
        if plat is None or plat == '': plat = 'BTH'
        self.PLAT_COINS[plat][prev_key] = row
        # This one is deprecated since we want to use the PLATFORM specific version every time ...
        #   ... but that will have to wait for corrective coding later on where this dict is used.
        self.SHEETS['CoinMiners'][prev_key] = row

        return row, prev_key

    # Configurations from ansible
    def setup_ansible_config(self):
        ansibleFilename = '/etc/ansible/hosts'
        self.ANSIBLE_HOSTS = { }
   
        try:
            # jprops does a good job of handling the minutiae of parsing a properties file, but
            #   it does not handle sections. So we use a hacky wrapper on jprops to do that.
            lines = open(ansibleFilename).read().splitlines()
            section = 'default'
            fo = open('/var/local/ramdisk/ansible.'+section+'.ini', 'w')
            for line in lines:
                regex = re.compile(r'[[]([^]]*)[]]', re.DOTALL)
                match = regex.match(line)
                if match:
                    fo.close()
                    section = match.group(1)
                    fo = open('/var/local/ramdisk/ansible.'+section+'.ini', 'w')
                else:
                    fo.write(line+"\n")
            fo.close()

            ansibleMinersFilename = '/var/local/ramdisk/ansible.miners.ini'
            with open(ansibleMinersFilename) as fh:
                for ip, value in jprops.iter_properties(fh):
                    (hostname, platform) = value.strip().split(' ')
                    hostname = hostname.split('=')[1]
                    platform = platform.split('=')[1]
                    self.ANSIBLE_HOSTS[hostname] = {'hostname': hostname, 'platform': platform, 'ip': ip}

        except IOError as ex:
            print(str(ex))
        except AttributeError as ex:
            print(ansibleFilename+' format is invalid (for miners).' + str(ex))
        except:
            print ( sys.exc_info()[0] )

        if self.VERBOSE: print(ansibleFilename+': '+str(self.ANSIBLE_HOSTS))

    # Find the given ticker in the CoinMiners table for this PLATFORM
    #   Return None if not found
    #   If verbose=True: print error message if not found
    def findTickerInPlatformCoinMiners(self, ticker, verbose=False):
        if ticker and ticker in self.PLAT_COINS[self.PLATFORM]:
            return self.PLAT_COINS[self.PLATFORM][ticker]
        if self.PLATFORM == 'BTH':
            return self.findTickerInCoinMiners(ticker, verbose)
        if verbose: print ("Coin '" + ticker + "' is not configured for this platform='"+self.PLATFORM+"'.", file=sys.stderr)
        return None

    # Find the given ticker in the CoinMiners table, regardless of PLATFORM
    #   Return None if not found
    #   If verbose=True: print error message if not found
    def findTickerInCoinMiners(self, ticker, verbose=False):
        if ticker and ticker in self.SHEETS['CoinMiners']:
            return self.SHEETS['CoinMiners'][ticker]
        if verbose: print ("Coin '" + ticker + "' is not configured in miners.xslx/CoinMiners.", file=sys.stderr)
        return None


    def substitute(self, row_id, arg):
        rslt = arg
        conf = self.SHEETS['CoinMiners'][row_id]
        # Substitute in reverse sequence of name's length
        keys = conf.keys() ; keys.sort(key=lambda item: (-len(item), item))
        for trans in xrange(0,2): # loop thrice to enable transitive substitutions
            if trans>9:
                print(rslt)
            for key in keys:
                val = conf[key]
                if val == '': continue
                # Substitute both '$NAME" and '<NAME>'
                rslt = rslt.replace('$'+key,val).replace('<'+key+'>',val)
        return rslt
