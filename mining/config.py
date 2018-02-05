import xlrd

class Config(object):

    MINERS_XLSX = '/opt/mining/miners.xlsx'
    ALL_MEANS_ONCE = -11111

    SHEETS = {
        'CoinMiners': None,
        'Clients': None
        }
    
    SUBSTITUTIONS = {
        'COIN': 'CoinMiners/Coin',
        'MINER': 'CoinMiners/Miner',
        'CONFIG_FILE': 'CoinMiners/ConfigFile',
        'URL_PORT': 'CoinMiners/UrlPort',
        'USER_PASSWORD': 'CoinMiners/UserPassword',
        'WALLET': 'CoinMiners/Wallet',
        'OPTIONS': 'CoinMiners/Options,Clients/Options',
        'ENVIRONMENT': 'CoinMiners/Environment,Clients/Environment',
        'MNEMONIC': 'Clients/Mnemonic',
        'PLATFORM': 'Clients/Platform',
        'EXECUTABLE': 'Clients/Executable',
        'CHDIR': 'Clients/chdir'
        }

    def substitute(self, coin, arg):
        rslt = arg
        for key in self.SUBSTITUTIONS:
            keys = self.SUBSTITUTIONS[key].split('/')
            # We substitute both '$NAME" and '<NAME>'
            rslt = arg.replace('$'+key,self.SHEETS[keys[0]][coin][key[1]]).replace('<'+key+'>',self.SHEETS[keys[0]][key[1]])
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
        self.stats_dict = {}
        self.StatsUrls = {}
        self.ConvertUrls = {}
        self.coin_dict = {}
        self.client_dict = {}
    
        self.setup_stats_dict()
        return
  
  
    def setup_stats_dict(self):
  
        ### openpyxl might be better for accessing miners.xlsx; at least it reads hyperlinks,
        ### but it does deserialize into an odd structure, so we'll pick out what we need here
        ''' EXCEPT THAT IT KEEPS FAILING RANDOMLY!
        IT IS ALSO WHY miners STARTUP HAS BEEN SO SLOW RECENTLY.
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
        '''

        # Put Stats sheet into stats_dict
        workbook = xlrd.open_workbook(self.MINERS_XLSX)
        sheet = workbook.sheet_by_name('stats')
        keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
        for row_index in xrange(1, sheet.nrows):
            d = {keys[col_index]: sheet.cell(row_index, col_index).value 
                 for col_index in xrange(sheet.ncols)}
            key = d['COIN']
            self.stats_dict[key] = d
      
        # Put Coin sheet into coin_dict
        sheet = workbook.sheet_by_name('CoinMiners')
        # read header values into the keys list    
        keys = [sheet.cell(0, col_index).value for col_index in xrange(sheet.ncols)]
        pd = {}
        for row_index in xrange(1, sheet.nrows):
          
            d = {keys[col_index]: sheet.cell(row_index, col_index).value 
                 for col_index in xrange(sheet.ncols)}
        
            d['OPTIONS']=''
            if not d['COIN'].strip() :
                pd['OPTIONS'] = d['MINER']
                self.coin_dict[pd['COIN']] = pd
            else:
                key = d['COIN']
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
            key = d['MNEMONIC']
            self.client_dict[key] = d

        return [self.stats_dict,self.StatsUrls,self.ConvertUrls,self.coin_dict,self.client_dict]
