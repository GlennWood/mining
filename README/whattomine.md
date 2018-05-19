whattomine
==========


Queries [WhatToMine](https://whattomine.com) for profitability of your rig(s) (as configured in *miners.xslx/WhatToMine*). It lists the top five (5) coins to mine, with a percentage difference listed (each percent in relation the next higher profitable coin). A **-v** option will list all coins from [WhatToMine](https://whattomine.com) rather than just the top five.

A *--scope <parm>* option will query all of your rigs and produce a report for each. The *<parm>* part may be *all*, which reports on all your rigs, or some other string which will limit the report to your rigs whose name contains the given *<parm>* string (case-insensitive). 


* Example

        $> miners whattomine
        ZEC,7.81,6.66,0%,0%
        ZEN,7.33,6.18,-6%,-7%
        RVN,7.24,6.04,-1%,-2%
        BSD,7.18,6.03,0%,0%
        ZCL,6.94,5.79,-3%,-3%
Next to the coin's symbol, the next two numbers are the 24hr revenue and profitability of the coin. The two percentages are the revenue and profitability compared to the coin immediately above (not relative to the top coin).

        $> miners whattomine --scope all
        [rig-AMD]       ETH 12.89    0%  MUSIC 10.67  -21%   ELLA 10.28   -4%    ETP 10.18   -1% 
        [rig-BORG]      ZEC  7.83    0%    ZEN  7.30   -7%    RVN  7.25   -1%    BSD  7.21    0% 
        [rig-NVI]       ZEC 14.67    0%    ZEN 13.68   -8%    ZCL 13.05   -5%    ETH 12.86   -2% 
        [rig-Titans] ssh: connect to host 10.0.0.8 port 22: No route to host;
        TOTALS:             35.39    0%        31.65  -11%        30.58   -3%        30.25   -1% 
Each rig's numbers are listed on a single line. The *--scope* report is refined a bit, reporting only the revenue (not profit) dollar amount, and the relative percent of the profit (not revenue). This makes a bit more sense, and more concise, when using these numbers for a heuristic assessment of which coins to mine.
