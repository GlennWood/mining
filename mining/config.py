import xlrd
import re

class Config(object):

    MINERS_XLSX = '/opt/mining/miners.xlsx'
    ALL_MEANS_ONCE = -11111

    SHEETS = {
        'CoinMiners': None,
        'Clients': None
        }
    

    def substitute(self, row_id, arg):
        rslt = arg
        conf = self.SHEETS['CoinMiners'][row_id]
        # Substitute in reverse sequence of name's length
        keys = conf.keys() ; keys.sort(key=lambda item: (-len(item), item))
        for key in keys:
            val = conf[key]
            if val == '': continue
            # Substitute both '$NAME" and '<NAME>'
            rslt = rslt.replace('$'+key,val).replace('<'+key+'>',val)
        return rslt

    def get_arguments(self):
        return self.arguments
  
    def __init__(self, argumentsIn):
        self.arguments = argumentsIn
        
        # Command line options
        self.ALL_COINS = self.arguments['COIN'] is None or len(self.arguments['COIN']) == 0
        self.VERBOSE = self.arguments['-v']
        if '--print' in self.arguments:
            self.PRINT = self.arguments['--print']
        else: self.PRINT = False
        if '--dryrun' in self.arguments:
            self.DRYRUN = self.arguments['--dryrun']
        else: self.DRYRUN = False

        # Variables
        self.WORKER_NAME = ''
        self.StatsUrls = {}
        self.ConvertUrls = {}
    
        self.setup_stats_dict()
        return
  
  
    def setup_stats_dict(self):

        # Put Stats sheet into stats_dict
        workbook = xlrd.open_workbook(self.MINERS_XLSX)
        for sheet_name in workbook.sheet_names():
            sheet = workbook.sheet_by_name(sheet_name)
            self.SHEETS[sheet_name] = {}
            keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
            prev_key = ''
            for row_index in xrange(1, sheet.nrows):
                row = {keys[col_index]: sheet.cell(row_index, col_index).value 
                     for col_index in xrange(sheet.ncols)}

                # The CoinMiners sheet has a special way of enabling a wider OPTIONS cell
                if sheet_name == 'CoinMiners':
                    row['OPTIONS']='' # There is no OPTIONS column native to the CoinMiners sheet
                    if not row['COIN'].strip() :
                        #row['COIN'] = prev_key
                        self.SHEETS[sheet_name][prev_key]['OPTIONS'] = row['MINER']
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

                prev_key = row[keys[0]].upper()
                self.SHEETS[sheet_name][prev_key] = row

        if self.ALL_COINS: 
            self.arguments['COIN'] = [x.upper() for x in sorted(list(self.SHEETS['CoinMiners'].keys()))]   

        return [self.SHEETS['Stats'],self.StatsUrls,self.ConvertUrls,self.SHEETS['CoinMiners'],self.SHEETS['Clients']]
