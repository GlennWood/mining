import openpyxl
import xlrd

class Config(object):

    def get_arguments(self):
        return self.arguments
  
    def __init__(self, argumentsIn):
        self.arguments = argumentsIn

        # Constants
        self.MINERS_XLSX = '/opt/mining/miners.xlsx'
        self.ALL_MEANS_ONCE = -11111

        # Command line options
        self.VERBOSE = self.arguments['-v']
        self.PRINT = self.arguments['--print']
        self.ALL_COINS = self.arguments['COIN'] is None or len(self.arguments['COIN']) == 0
        #self.DRYRUN = ''
        self.DRYRUN = self.arguments['--dryrun']

        # Variables
        self.WORKER_NAME = ''
        self.stats_dict = {}
        self.StatsUrls = {}
        self.ConvertUrls = {}
        self.coin_dict = {}
        self.client_dict = {}
        self.stats_sheet = {}
    
        self.setup_stats_dict()
        return
  
  
    def setup_stats_dict(self):
  
        ### openpyxl might be better for accessing miners.xlsx; at least it reads hyperlinks,
        ### but it does deserialize into an odd structure, so we'll pick out what we need here
        wb = openpyxl.load_workbook(filename = self.MINERS_XLSX)
        self.stats_sheet = wb['stats']
        idx = 1
        for coin in self.stats_sheet['A']:
            if not coin.value is None: 
                self.stats_dict[coin.value] = self.stats_sheet['A'+str(idx)+':C'+str(idx)]
                val = self.stats_dict[coin.value][0][1]
                if val and val.hyperlink:
                    self.StatsUrls[coin.value] = (val.value,val.hyperlink.display)
                val = self.stats_dict[coin.value][0][2]
                if val and val.hyperlink:
                    self.ConvertUrls[coin.value] = (val.value,val.hyperlink.display)
                idx += 1
      
        # Put Stats sheet into stats_dict
        workbook = xlrd.open_workbook(self.MINERS_XLSX)
        sheet = workbook.sheet_by_name('stats')
        keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
        for row_index in xrange(1, sheet.nrows):
            d = {keys[col_index]: sheet.cell(row_index, col_index).value 
                 for col_index in xrange(sheet.ncols)}
            key = d['Coin']
            self.stats_dict[key] = d
      
        # Put Coin sheet into coin_dict
        sheet = workbook.sheet_by_name('CoinMiners')
        # read header values into the keys list    
        keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
        pd = {}
        for row_index in xrange(1, sheet.nrows):
          
            d = {keys[col_index]: sheet.cell(row_index, col_index).value 
                 for col_index in xrange(sheet.ncols)}
        
            d['Options']=''
            if not d['Coin'].strip() :
                pd['Options'] = d['Miner']
                self.coin_dict[pd['Coin']] = pd
            else:
                key = d['Coin']
                self.coin_dict[key.upper()] = d
                pd = d

        if self.ALL_COINS: 
            self.arguments['COIN'] = [x.upper() for x in sorted(list(self.coin_dict.keys()))]   
        
        # Put Client mnemonics sheet into client_dict
        sheet = workbook.sheet_by_name('Clients')
        keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
        self.client_dict = {}
        for row_index in xrange(1, sheet.nrows):
            d = {keys[col_index]: sheet.cell(row_index, col_index).value 
                 for col_index in xrange(sheet.ncols)}
            key = d['Mnemonic']
            self.client_dict[key] = d

        return [self.stats_dict,self.StatsUrls,self.ConvertUrls,self.coin_dict,self.client_dict]
