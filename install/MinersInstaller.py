from __future__ import print_function
import sys
import os
import re
import cmd
import shutil

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
        if pkgs:
            for pkg in pkgs:
                if pkg.startswith('pip ') or pkg.startswith('pip2 ') or pkg.startswith('pip3 '):
                    pip, pakg = pkg.split(' ')
                    MinersInstaller.PKGS[pakg] = pip
                    # TODO install with pip when we see this.
                else:
                    MinersInstaller.PKGS[pkg] = 'apt'

        if isinstance(commands, str):
            self.COMMANDS = [ commands ]
        else:
            self.COMMANDS = commands
          
        MinersInstaller.INSTALLERS.append(self)

    @classmethod
    def install_pkgs(slf, config):
        if  not MinersInstaller.PKGS or len(MinersInstaller.PKGS) is 0:
            return
        # The dict nature of self.PKGS insures each package is installed only once
        pkgsCmd = 'apt-get -y install '+' '.join(MinersInstaller.PKGS.keys())
        if config['--dryrun']:
            if MinersInstaller.PKGS:
                print(pkgsCmd)
        else:
            if MinersInstaller.PKGS:
                RC = os.system(pkgsCmd)
                if RC:
                    sys.exit(RC)
        MinersInstaller.PKGS = None

    @classmethod
    def install_all(slf, config):
        # Install all dependant packages first
        MinersInstaller.install_pkgs(config)
        for installer in MinersInstaller.INSTALLERS:
            installer.install(config)
       
    def install(self, config):

        if config['--dryrun']:
            print('cd /opt')
        else:
            os.chdir('/opt')

        if self.SOURCE:
            srcDir = self.SOURCE.split('/')
            srcDir = srcDir[-1].replace('.git','')
            srcDir = self.get_source(config, self.SOURCE, srcDir)
            if not config['--dryrun']:
                print("Starting installation of "+self.NAME+' in '+srcDir)

        self.RC = 0
        for cmd in self.COMMANDS:
            if cmd.startswith('cd '):
                if config['--dryrun']:
                    print(cmd)
                else:
                    self.RC = os.chdir(cmd.replace('cd ',''))
                    if self.RC:
                        print("FAIL: '"+cmd+"' returned RC="+self.RC)
                        break
            elif cmd.startswith('mkdir '):
                if config['--dryrun']:
                    print(cmd)
                else:
                    dirs = cmd.split(' ')
                    dirs.pop(0)
                    for nDir in dirs:
                        if os.path.isdir(nDir):
                            shutil.rmtree(nDir)
                        os.mkdir(nDir)
            elif cmd.startswith('export '):
                if config['--dryrun']:
                    print(cmd)
                else:
                    exports = cmd.split(' ')
                    exports.pop(0)
                    for export in exports:
                        key,val = export.split('=')
                        os.environ[key] = val
            elif cmd.startswith('install-'):
                cmd = os.getenv('MINING_ROOT','/opt/mining')+'/install/'+cmd
                if config['--dryrun']:
                    print(cmd)
                else:
                    os.system(cmd)
            elif cmd.startswith('ln '):
                if config['--dryrun']:
                    print(cmd)
                else:
                    parms = cmd.split(' ')
                    if os.path.lexists(parms[3]):
                        os.remove(parms[3])
                    os.symlink(parms[2], parms[3])
            else:
                if config['--dryrun']:
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
            if not config['--dryrun']:
                print("Finished installation of "+self.NAME)
            print("Exiting due to errors, RC="+str(self.RC))
            sys.exit(self.RC)

        return 0

    def get_source(self, config, git_repo, srcDir):

        if config['--dryrun']:
            if self.SOURCE.startswith('wget '):
                print(self.SOURCE)
            else:
                if os.path.isdir(srcDir):
                    print('cd '+srcDir)
                    print('git pull '+git_repo+' -C '+srcDir)            
                else:
                    print('git clone '+self.SOURCE)
                    print('cd '+srcDir)
            return srcDir

        dirName = None
        if self.SOURCE.startswith('wget '):
            self.RC = os.system(self.SOURCE)
            if self.RC:
                sys.exit(1)
            archiveName = self.SOURCE.split('/')[-1]
            if archiveName.endswith('.tgz') or archiveName.endswith('.tar.gz'):
                os.system('tar -xzf '+archiveName)
                dirName = archiveName.replace('.tgz','').replace('.tar.gz','')
            if archiveName.endswith('.txz') or archiveName.endswith('.tar.xz'):
                os.system('tar --xz -xf '+archiveName)
                dirName = archiveName.replace('.txz','').replace('.tar.xz','')
            elif archiveName.endswith('.tar.lrz'):
                os.system('lrunzip '+archiveName)
                archiveName = archiveName.replace('.lrz','')
                os.system('lrunzip '+archiveName)
                dirName = archiveName.replace('.tar','')
            if dirName:
                if not os.path.isdir(dirName):
                    dirName = dirName.replace('-amd64','')
                os.chdir(dirName)
            return dirName
       
        regex = re.compile(r'.*?/([^/]*)[.]git')
        match = regex.match(git_repo)
        if match != None:
            dirName = match.group(1)
        else:
            dirName = self.NAME

        if os.path.isdir(srcDir):
            os.chdir(srcDir)
            self.RC = os.system('git pull')            
        else:
            self.RC = os.system('git clone '+git_repo)
            if self.RC is 0:
                self.RC = os.chdir(srcDir)
        if self.RC:
            print("'git clone "+git_repo+"' failed.",file=sys.stderr)
            sys.exit(1)
       
        return dirName
