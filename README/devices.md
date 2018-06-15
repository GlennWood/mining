miners devices
==============

`miners devices` lists the temperature, power consumption and speed of the devices (GPUs) on your rig. 

    rig-AMD:~$ miners devices
    AMD1 74C 116W 2250Mhz
    AMD2 74C 139W 2000Mhz
    AMD3 74C 110W 2000Mhz
    AMD4 75C 123W 1750Mhz
    AMD5 74C 140W 1750Mhz
    AMD6 75C 126W 2000Mhz
    AMD7 78C 134W 2000Mhz
    AMD8 74C 136W 2000Mhz
    TOTAL: 1024 watts (AMD)
    TOTAL: 1024 watts

With option `--verbose` it will list the type and GUID of the devices as well.
 
        rig-Nvidia:~$ miners devices --verbose
        NVI0: 82C 119W GeForce GTX 1070 GPU-3e321474-214c-c305-a479-255a616c8e35
        NVI1: 73C  95W GeForce GTX 1070 GPU-990059da-5633-1178-e4fe-f1f7fc50ad61
        NVI2: 82C 110W GeForce GTX 1070 GPU-b9e933d0-5c48-19d3-2765-64cd8f54b7db
        NVI3: 82C  94W GeForce GTX 1070 GPU-3fbd9994-bdfc-dc17-45ec-e691f3ad4a17
        NVI4: 69C 144W GeForce GTX 1070 GPU-3768179a-d438-0c05-de32-7f38e9af63f1
        NVI5: 82C  79W GeForce GTX 1070 GPU-22d50ff2-2ae8-6e7f-b9fb-e6be717fa79b
        NVI6: 81C 151W GeForce GTX 1070 Ti GPU-048ac11c-24be-8e3f-059e-2028689fb9cb
        NVI7: 81C 157W GeForce GTX 1070 Ti GPU-7cac86c5-b598-6294-149c-a53e0df86019
        TOTAL: 949 watts (NVI)
        TOTAL: 949 watts
