fabric_tasks
============

Collection of Python Fabric Tasks

freepbx-12.py
=============

**Bootstrapping a Centos 6.6 VM**

Do this on a CLEAN vanillla install of Centos. Don't do this on an existing server. All you need is networking enabled with an IP to use this bootstrap proccess.

Prior to installing Asterisk 12 and FreePBX, there are some updates and modifications that need to be made to the Centos 6.6 VM or Server. Running this command with the correct IP address should address those needs and reboot the server.

<code>fab --colorize-errors -f freepbx-12.py bootstrap:ip=192.168.1.10,hostname=peanutbutterxray.dev.local</code>

This will:

* install epel
* update the system
* install all needed libraries
* change the dir color from blue to yellow
* disable iptables
* disable selinux
* install and enable mysql
* install and enable apache
* install peardb
* set the hostname
* install XenTools if available
* reboot
 
NOTE: You will want to re-enable and configure IPTABLES and SELINUX to fit your environment. They are outside the scope of this installer as each environment is different.

**Installing Asterisk and FreePBX**

NOTE: You will want to change the db password in the script before running it. I could automate it, but I have no interest in doing so. Search for 'amp109'.

This should download and install all dependencies of Asterisk 12 and FreePBX. Then it should build and install said programs and configure them. Once complete FreePBX should be available through http at the servers address.

<code>fab --colorize-errors -f freepbx-12.py install:ip=192.168.1.10</code>

This will:

* Download, Configure and build srtp
* Download, Configure and build pjproject
* Download, Configure and build jansson
* Download, Configure and build asterisk
* Download, Configure and build FreePBX

