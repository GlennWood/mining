miners balances
===============
`miners balances` will query web sources (exchanges and mining pools) and report your balances held there.

* Example

        rig-Nvidia:~$ miners balances 
        BLEUTRADE
          ETH 0.0438079
          BTG 0.37085029
          LTC 0.0
        CRYPTO-BRIDGE
          BTS 0.00521
          BTC 0.00001017
          RVN 2,814.7792
        CRYPTOPIA
          BTC 0.0025892
          ZCL 0.275625
        GDAX
          ETH 0.50202905
          BTC 0.0
          USD 0.00102938381635
          LTC 0.0
          BCH 0.0
        MININGPOOLHUB
          ETH 0.01066152
          XMR 0.00042143
          BTCP 0.0010778
        NICEHASH
          BTC 0.00423273
        OPEN-LEDGER
          FREECOIN 10,000.0000
        SUPRNOVA
          KMD 0.57365331
        UNIMINING
          GBX 0.0
          TZC KeyboardInterrupt

The sources are configured in the `/opt/mining/mining/balances/sources.yml` file, for example:

    SOURCES:
      BLEUTRADE:
        BTG:
        ETH: 
        LTC:
      CRYPTOPIA:
        all: cryptopia
      CRYPTO-BRIDGE:
        all: bit-shares
      GDAX: 
        all: gdax
      NICEHASH:
        all: https://api.nicehash.com/api?method=balance&id=$API_ID&key=$API_KEY
      MININGPOOLHUB:
        all: https://miningpoolhub.com/index.php?page=api&action=getuserallbalances&api_key=$API_KEY
      UNIMINING:
        GBX: https://www.unimining.net/api/walletEx?address=$API_ID
        TZC: https://www.unimining.net/api/walletEx?address=$API_ID
      SUPRNOVA:
        KMD: https://kmd.suprnova.cc/index.php?page=api&action=getuserbalance&api_key=$API_KEY&id=$API_ID
      OPEN-LEDGER:
        all: bit-shares

The `SOURCES` section has an element for each source, which might be an exchange or a mining pool (somewhere that currencies might be held). Each source element lists the coins held there (`all` might work for some sources to specify any and all coins, while other sources require an explicit list of coins). Each such coin may further designate an URL, or another mechanism, for obtaining the balance(s). The "other mechanisms" are hardcoded into `/opt/mining/mining/balances/__init__.py`
Note that the URLs listed in this example `sources.yml` include `$API_ID`, `$API_KEY`, etc. These will be substituted from values found *hidden*, by you, in your own `/home/$MINERS_USER/.ssh/mining-keys/<source>-<coin>.key` files. For instance:

    cat /home/albokiadt/.ssh/mining-keys/nicehash.key 
    {
        "api_id": "<YOUR-NICEHASH-API-ID>",
        "api_key": "<YOUR-NICEHASH-API-KEY>"
    }
or

    cat /home/$MINERS_USER/.ssh/mining-keys/bleutrade-eth.key
    {
        "api_id": "<YOUR-BLEUTRADE-API-ID>",
        "api_key": "<YOUR-BLEUTRADE-API-KEY>",
        "api_secret": "<YOUR-BLEUTRADE-API-SECRET>"
    }
    
And yes, the URLs specify the API_<?> parameters in uppercase, and the mining-keys files are named in lowercase and contain all lowercase field names.

Scoping
-------
You may limit the scope of the balances report to a subset of the sources, just as you would specify a single source.

* Type of source

The type of sources is configured in the `SCOPING` section of `sources.yml`, where we might see

    SCOPING:
      MINING: [ MININGPOOLHUB, NICEHASH, SUPRNOVA, UNIMINING ]
      EXCHANGING: [ BLEUTRADE, CRYPTOPIA, CRYPTO-BRIDGE, OPEN-LEDGER ]
      BANKING: [ GDAX ]

So, to limit the report to MINING sources.

        rig:~$ miners balances mining

* Type of source and coin(s)

You may also limit the report to just one or more coins within a scope of sources, as in:

        rig:~$ miners balances mining:rvn,eth

which would list the balances of RVN and ETH currencies in each MINING source.

* `COMMON_TO_SYMBOL`

Just FYI, you will also find a `COMMON_TO_SYMBOL` section in `sources.yml`. This is there to help `miners balances` parse common currency names in some result sets from sources into ticker symbols.

    COMMON_TO_SYMBOL:
      bitcoin-private: BTCP
      ethereum-classic: ETC
      bitcoin-gold: BTG
      ethereum: ETH
      expanse: EXP
      monero: XMR
      zcash: ZEC
      musicoin: MUSIC
      zclassic: ZCL
      zencash: ZEN

These are just a few of them, as used by your author, and you should add to `COMMON_TO_SYMBOL` if you require more.