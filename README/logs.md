miners logs
==============

`miners logs` will tail the log files of the currently running miner.  `miners logs` will tail the given coin's log files, regardless if it is currently running.

    rig-AMD:~$ miners logs eth
    ==> /var/log/mining/A-ETC-miner.log <==
	ETH: 06/20/18-18:53:09 - SHARE FOUND - (GPU 7)
	ETH: Share accepted (17 ms)!
	GPU0 t=74C fan=20%, GPU1 t=74C fan=60%, GPU2 t=74C fan=81%, GPU3 t=75C fan=22%, GPU4 t=73C fan=32%, GPU5 t=75C fan=28%, GPU6 t=76C fan=62%, GPU7 t=73C fan=58%
	ETH: 06/20/18-18:53:20 - New job from us-east.ethash-hub.miningpoolhub.com:20555
	ETH - Total Speed: 201.045 Mh/s, Total Shares: 712, Rejected: 0, Time: 04:30
	ETH: GPU0 30.642 Mh/s, GPU1 22.159 Mh/s, GPU2 27.168 Mh/s, GPU3 22.206 Mh/s, GPU4 22.191 Mh/s, GPU5 22.155 Mh/s, GPU6 27.250 Mh/s, GPU7 27.274 Mh/s
	ETH: 06/20/18-18:53:34 - New job from us-east.ethash-hub.miningpoolhub.com:20555
	ETH - Total Speed: 201.092 Mh/s, Total Shares: 712, Rejected: 0, Time: 04:30
	ETH: GPU0 30.675 Mh/s, GPU1 22.166 Mh/s, GPU2 27.167 Mh/s, GPU3 22.194 Mh/s, GPU4 22.189 Mh/s, GPU5 22.172 Mh/s, GPU6 27.273 Mh/s, GPU7 27.256 Mh/s
	GPU0 t=74C fan=20%, GPU1 t=74C fan=60%, GPU2 t=74C fan=82%, GPU3 t=75C fan=23%, GPU4 t=73C fan=32%, GPU5 t=75C fan=29%, GPU6 t=77C fan=63%, GPU7 t=73C fan=58%
	
	==> /var/log/mining/A-ETC-miner.err <==

Option `--scope` helps you refine the output a bit. It accepts and regular expression and will print only those lines of the logs that match it. Also, some patterns are preconfigured so you can you a mnemonic, such as `--scope temp`:

    rig-Nvidia:~$ miners logs --scope temp
    58,66,63,62,64,62,62
    64,74,70,66,73,68,67
    67,78,75,66,78,70,70
    68,81,78,66,80,72,70
    69,82,80,66,82,72,71
    69,82,81,66,82,73,71
    69,82,82,66,82,73,71
    69,82,82,67,82,73,71
    ...

Specify `--scope '.*Total Speed.*'` and you will get the lines reporting the total speed.

    rig-AMD:~$ miners logs --scope '.*Total Speed.*'
    ETH - Total Speed: 201.064 Mh/s, Total Shares: 77, Rejected: 0, Time: 00:28
    ETH - Total Speed: 201.207 Mh/s, Total Shares: 79, Rejected: 0, Time: 00:28
    ...

Be creative ...

    rig-AMD:~$ miners logs --scope '.*Total Speed[^,]*'
    ETH - Total Speed: 191.414 Mh/s
    ETH - Total Speed: 191.337 Mh/s
    ...

That one is also provided by `--scope speed`.

Configuration file `logs.yml`
-----------------------------
Note that the scopes are configured in `/opt/miners/conf/logs.yml` and you may add your own there:

    rig-NVI:~$ cat /opt/miners/conf/logs.yml
    SCOPES:
      speed:
        - '.*(Total Speed[^,]*)'
        - 'GPU #[0-9.,]*: [0-9.,]* [GMKgmk][Hh]z'
        - '.*(GPU #[0-9]*: [^,]*, [0-9.,]* [GMKgmk][Hh]/s)'
      temp:
        - ' t=([0-9]*)C'

Each scope has a name, and an array of regular expressions associated with it. If any one (or more) regexes match a line of the log file(s) then they are printed.