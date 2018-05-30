
Ansible for *GlennWood/mining* rigs
=================================

**Overview**

*ansible* is installed by *install/install-1st*. There is currently only one playbook, in */etc/ansible/playbooks/sync-mining-rigs.yml*. 
It synchronizes the content of three folders, */opt/mining*, */etc/mining* and */etc/ansible/*, on all your mining rigs.
*sync-mining-rigs* is a command-line alias for *ansible-playbook /opt/mining/ansible/playbooks/sync-mining-rigs.yml*

**Configuration**

Configure *ansible* with all your mining rigs names, IP addresses and platforms in */etc/ansible/hosts*. You should stick to the stricter format illustrated by */etc/ansible/hosts-eq*, since this *hosts* file is also parsed by other scripts in the *GlennWood/mining* suite.

**Sanity Check**

    ansible all -m ping  --ask-pass -c paramiko

**Install PKI keys**

To enable passwordless logins for *ansible*, create and install PKI keys on all your miners. Log into any one of your miners and create the PKI pair with:

    ssh-keygen

This will ask for a new passphrase but we do not need one, so just enter a blank line when asked for passphrase.

Then insert the public key into each miner's *authorized_keys* file with:

    ansible all -m authorized_key -a "user=$MINERS_USER key='{{ lookup('file', '/home/$MINERS_USER/.ssh/id_rsa.pub') }}' \
        path /home/$MINERS_USER/.ssh/authorized_keys manage_dir=no" --ask-pass -c paramiko

Once that is done we do not need a password to log into any of your mining rigs from this mining rig. To be able to login *from* others rigs into your rigs, run these commands now.

    ansible all -m copy -a "src=/home/$MINERS_USER/.ssh/id_rsa dest=/home/$MINERS_USER/.ssh/id_rsa" --ask-pass -c paramiko
    ansible all -m copy -a "src=/home/$MINERS_USER/.ssh/id_rsa.pub dest=/home/$MINERS_USER/.ssh/id_rsa.pub" --ask-pass -c paramiko

** Synchronize Mining Rigs **

    