#!/usr/bin/python
from __future__ import print_function
import sys
import os
import re
import cmd
import shutil
sys.path.insert(0,'/opt/mining/mining')

class MinersInstaller():

    PKGS = {}
    INSTALLERS = []

    def __init__(self, miner_config):
        name = miner_config[0]
        source= miner_config[1]
        pkgs= miner_config[2]
        commands= miner_config[3]

        self.NAME = name
        self.SOURCE = source
        for pkg in pkgs:
            if pkg.startswith('pip '):
                MinersInstaller.PKGS[pkg.split(' ')[1]] = 'pip'
                # TODO install with pip when we see this.
            else:
                MinersInstaller.PKGS[pkg] = 'apt'
        self.COMMANDS = commands
        MinersInstaller.INSTALLERS.append(self)

    @classmethod
    def install_pkgs(slf, config):
        # The dict nature of self.PKGS insures each package is installed only once
        if config.DRYRUN:
            print (MinersInstaller.PKGS)
            print('apt-get -y install '+' '.join(MinersInstaller.PKGS.keys()))
        else:
            RC = os.system('apt-get -y install '+' '.join(MinersInstaller.PKGS.keys()))
            if RC:
                sys.exit(RC)
        MinersInstaller.PKGS = []

    @classmethod
    def install_all(slf, config):
        # Install all dependant packages first
        MinersInstaller.install_pkgs(config)
        for installer in MinersInstaller.INSTALLERS:
            installer.install(config)
       
    def install(self, config):

        srcDir = self.SOURCE.split('/')
        srcDir = srcDir[len(srcDir)-1].replace('.git','')
        if config.DRYRUN:
            print('git clone '+self.SOURCE)
            print('cd '+srcDir)
        else:
            repoName = self.git_clone(self.SOURCE, srcDir)
            os.chdir('/opt/'+repoName)
            print("Starting installation of "+self.NAME)

        self.RC = 0
        for cmd in self.COMMANDS:
            if cmd.startswith('cd '):
                if config.DRYRUN:
                    print(cmd)
                else:
                    self.RC = os.chdir(cmd.replace('cd ',''))
                    if self.RC:
                        print("FAIL: '"+cmd+"' returned RC="+self.RC)
                        break
            elif cmd.startswith('mkdir '):
                if config.DRYRUN:
                    print(cmd)
                else:
                    dirs = cmd.split(' ')
                    dirs.pop(0)
                    for nDir in dirs:
                        if os.path.isdir(nDir):
                            shutil.rmtree(nDir)
                        os.mkdir(nDir)
            elif cmd.startswith('ln '):
                if config.DRYRUN:
                    print(cmd)
                else:
                    parms = cmd.split(' ')
                    if os.path.lexists(parms[3]):
                        os.remove(parms[3])
                    os.symlink(parms[2], parms[3])
            else:
                if config.DRYRUN:
                    print(cmd)
                else:
                    self.RC = os.system(cmd)
                    if self.RC:
                        print("FAIL: '"+cmd+"' returned RC="+str(self.RC))
                        break
        #[ -n "$RUN_ALL_TESTS" ] && ./ccminer --algo=neoscrypt --benchmark
        if self.RC != 0:
            with open('/etc/profile.d/'+self.NAME+'.sh','a+') as fh:
                fh.write("export INSTALL_"+self.NAME.upper().replace('-','_')+"_DONE=`date --utc +%Y-%m-%dT%H-%M-%SZ`\n")
            if not config.DRYRUN:
                print("Finished installation of "+self.NAME)
            print("Exiting due to errors, RC="+str(self.RC))
            sys.exit(self.RC)

        return 0

    def git_clone(self, git_repo, srcDir):

        regex = re.compile(r'.*?/([^/]*)[.]git', re.DOTALL)
        match = regex.match(git_repo)
        if match != None:
            repoName = match.group(1)
        else:
            repoName = self.NAME

        if os.path.isdir(srcDir):
            self.RC = os.system('git pull '+git_repo+' -C '+srcDir)            
        else:
            self.RC = os.system('git clone '+git_repo)
        if self.RC:
            os.chdir('/opt/'+repoName)
            self.RC = os.system('git pull')
            if self.RC:
                #raise BaseException("FAIL: git clone "+git_repo)
                sys.exit(1)
        
        return repoName
