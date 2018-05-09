import requests
from lxml import html
#from lxml import etree

### http://whattomine.com/coins.json

'''
/html/body/div[@class='container']/table[@class='table table-hover table-vcenter']/tbody/tr
then interate over ./td ... [div/text()]
'''

def process(self, config, coin):

    url = "https://whattomine.com/coins?utf8=%E2%9C%93&adapt_q_280x=0&adapt_q_380=0&adapt_q_fury=0&adapt_q_470=0&adapt_q_480=3&adapt_q_570=0&adapt_q_580=0&adapt_q_vega56=0&adapt_q_vega64=0&adapt_q_750Ti=0&adapt_q_1050Ti=0&adapt_q_10606=0&adapt_q_1070=6&adapt_1070=true&adapt_q_1070Ti=2&adapt_1070Ti=true&adapt_q_1080=0&adapt_q_1080Ti=0&adapt_1080Ti=true&eth=true&factor%5Beth_hr%5D=241.0&factor%5Beth_p%5D=990.0&grof=true&factor%5Bgro_hr%5D=274.0&factor%5Bgro_p%5D=1020.0&factor%5Bphi_hr%5D=158.0&factor%5Bphi_p%5D=1040.0&cn=true&factor%5Bcn_hr%5D=5040.0&factor%5Bcn_p%5D=780.0&cn7=true&factor%5Bcn7_hr%5D=5040.0&factor%5Bcn7_p%5D=780.0&eq=true&factor%5Beq_hr%5D=3520.0&factor%5Beq_p%5D=960.0&lre=true&factor%5Blrev2_hr%5D=295000.0&factor%5Blrev2_p%5D=1020.0&ns=true&factor%5Bns_hr%5D=8100.0&factor%5Bns_p%5D=1020.0&tt10=true&factor%5Btt10_hr%5D=150.0&factor%5Btt10_p%5D=960.0&x16r=true&factor%5Bx16r_hr%5D=68.0&factor%5Bx16r_p%5D=1030.0&skh=true&factor%5Bskh_hr%5D=228.0&factor%5Bskh_p%5D=960.0&n5=true&factor%5Bn5_hr%5D=364.0&factor%5Bn5_p%5D=1020.0&xn=true&factor%5Bxn_hr%5D=25.2&factor%5Bxn_p%5D=960.0&factor%5Bcost%5D=0.1&sort=Profitability24&volume=0&revenue=24h&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=binance&factor%5Bexchanges%5D%5B%5D=bitfinex&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=cryptobridge&factor%5Bexchanges%5D%5B%5D=cryptopia&factor%5Bexchanges%5D%5B%5D=hitbtc&factor%5Bexchanges%5D%5B%5D=poloniex&factor%5Bexchanges%5D%5B%5D=yobit&dataset=NVI&commit=Calculate"
    response = requests.get(url)
    response.raise_for_status()
    tree = html.fromstring(response.content)
    wtmList = tree.xpath("/html/body/div[@class='container']/table[@class='table table-hover table-vcenter']/tbody/tr")
    cnt = 0
    for tr in wtmList:
        cnt += 1
        coinName = tr.xpath("td[1]/div[2]/a/text()")
        revenue_profit = tr.xpath("td[8]")
        if len(coinName) > 0:
            coinName, ticker = coinName[0].split('(')
            ticker = ticker.replace(')','')
            revenue = revenue_profit[0].xpath("text()")
            profit = revenue_profit[0].xpath("strong/text()")
            if profit[0].find('-') < 0: # Let's skip the ones with negative profit.
                revenue = revenue[0].replace('$','')
                profit = profit[0].replace('$','')
                print(ticker+","+revenue.strip()+","+profit.strip())
        if cnt >= 7 and not config.VERBOSE:
            break
    return config.ALL_MEANS_ONCE

def initialize(self, config, coin):
    return config.ALL_MEANS_ONCE

def finalize(self, config, coin):
    return config.ALL_MEANS_ONCE
