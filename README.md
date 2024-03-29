miners
======
Cryptocurrency mining rig(s), pools and exchanges management scripts, for Linux (especially Ubuntu 16.04).

Configured via an Excel workbook, *miners.xslx*, this facility includes operations to 

* **start/stop** mining clients, 
* display **logs** thereof, 
* **report** the best coins to mine (derived from [whattomine.com](https://whattomine.com)), 
* display your current **balances** (from your various wallets, pools and exchanges), 
* **overclock** automatically upon start of mining operation, configured per GPU and coin in *[overclock.yml](conf/overclock.yml)*.
* and **other** conveniences for the mining rig operator.

This project contains numerous installation scripts to help the operator provision a mining rig(s), from bare Ubuntu, through GPU drivers, and mining clients.

Command Line
------------
    miners OPERATION COIN [ OPTIONS ]

* OPERATION

The *miners* operation to perform. May be a comma-seperated list of operations. See below for details.

* COIN

One, or a comma-separated list of, coins for the operation. These coins' mining options are configured in the [*CoinMiners*](README/CoinMiners.md) sheet of *miners.xslx* file.

* *-X* or *--dryrun* option

The *--dryrun* (or *-X* for short) option will list the commands this *miners* command will execute. It will then not execute them. Some abbreviation of the commands is done by default; to see the fully spelled out commands add the *-v* option.


Operations
----------

* **start** *\<coin>*

Starts a process mining the coin(s) given on the command line. Which mining client, and its parameters, are configured in the [*miners.xslx/CoinMiners*](README/CoinMiners.md) spreadsheet.

* **stop** *\<coin>*

Stops all processes mining the given coin(s). This is the converse of **start**.

* **restart**

Restarts the most recently started mining operation.

* **swap** *\<oldCoin>:\<newCoin>*

Stops mining **\<oldCoin>**, waits for **status** to report it as stopped, then starts mining **\<newCoin>**.

* **logs** [ *\<coin>* ]

Tails the log files of all miners currently running on the rig. Add a **<coin>** parameter to tail the logs of the given coin, running or not.

* **status**
 
Reports what miners are running on the current rig.
A *--scope <parm>* option will query each of your rigs and produce a report of all.
The *<parm>* part may be *all*, which repors on all your rigs, or some other string which will limit the report to your rigs whose name contains the given *<parm>* string (case-insensitive).

* **devices**

Reports the temperature, power consumption, and type of each of the GPUs on the rig. A **-v** adds each GPU's UUID to the report.


* **overclock**

*overclock* will set under-voltage (or power-limit for Nvidia cards) and memory rate on all GPUs installed on a rig. These may also be set on a per-coin basis, and is also run automatically before each *miners start*.

See [README/overclock.md](README/overclock.md) for an understanding of how to configure your own GPUs per-coin in the *Overclock* sheet of *miners.xslx*.

* **balances**

*balances* is a work-in-progress. It is intended to query all your wallets, and/or various exchanges, on which you are holding coin. Its configuration is a very much a *"maybe-this-one-will-make-sense"*, and is not complete.

* **whattomine**

Queries [WhatToMine](https://whattomine.com) for profitability of your rig(s) (as configured in *miners.xslx/WhatToMine*). It lists the top five (5) coins to mine, with a percentage difference listed (each percent in relation the next higher profitable coin). A **-v** option will list all coins from [WhatToMine](https://whattomine.com) rather than just the top five.

A *--scope <parm>* option will query all of your rigs and produce a report for each. The *<parm>* part may be *all*, which reports on all your rigs, or some other string which will limit the report to your rigs whose name contains the given *<parm>* string (case-insensitive). 

The *--scope* report is refined down a bit, reporting only the revenue (not profit) dollar amount, and the relative percent of the profit (not revenue). This makes a bit more sense when using these numbers for a heuristic assessment of which coins to mine.

***TODO***
----------

* **stats**

*stats* is a work-in-progress. It is intended to query the pools on which rigs are mining to report the current rate of mining. Its configuration is a very much in a *"maybe-this-one-will-make-sense"* state, and is not complete.


Tab Completion
==============
*miners* offers command-line tab-completion, which means you type in 'miners ', then "tap tab twice". This pops up a list of operations you may enter. Type in the first one or two characters of an operation, hit tab again, and the rest of the operation's name is filled in for you.
Many operations offer tab-completion beyond this, as well. "Tap tab twice" to see the options you may add to an operation. Again, type in some leading characters, hit tab again, and the rest of that option is filled in.

More Help
=========
These README files help the operator utilize more of the features of this project.

* The [*miners.xslx*](README.minersXslx.md) Excel workbook
* [Installation Scripts](install/README.md)
* [Monit](README/monit.md) monitoring
* [Ansible](README/ansible.md) installation and configuration management

License
=======
MIT License                                        

Copyright (c) 2018 Glenn Wood

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The aforementioned copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.    

Disclaimer
==========
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.