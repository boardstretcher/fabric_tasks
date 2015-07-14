from fabric.api import *
import os, time, logging, re, sys
from pprint import *

# uncomment for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
pprint(locals())

epoch_time = int(time.time())
# https://raw.githubusercontent.com/boardstretcher/fabric_tasks/master/files/sources.list

def centos6(ip,hostname):
        """Update and configure a clean Centos 6.5 machine
        """
        env.user = 'root'
        with settings(host_string='{0}'.format(ip)):

                # disable selinux
                run('sed -i "s/\=enforcing/\=disabled/g" /etc/selinux/config')

                # initial centos repositories
                run('yum install -y epel-release')

                # update system
                run('yum update -y')
                run('yum remove -y vim-minimal')
                run('yum groupinstall -y core; yum -y groupinstall base;')
                run('yum install -y kernel-devel vim wget')

                # custom colors and history format
                run('sed -i "s/DIR\ 01\;34/DIR\ 40\;33/g" /etc/DIR_COLORS ')

                # temporary disable iptables
                run('service iptables stop')
                run('chkconfig iptables off')

                # set hostname
                run('echo "127.0.0.1 {0} localhost localhost.localdomain localhost4 localhost4.localdomain4" > /etc/hosts'.format(hostname))
                run('echo "::1 localhost localhost.localdomain localhost6 localhost6.localdomain6" >> /etc/hosts'.format(hostname))
                run('sed -i "s/HOSTNAME=localhost.localdomain/HOSTNAME={0}/g" /etc/sysconfig/network'.format(hostname))

                # set nameserver and search domain
                run('echo "search signs365.local" > /etc/resolv.conf')
                run('echo "nameserver 192.168.55.4" >> /etc/resolv.conf')

                # reboot
                reboot()
                print('ATTENTION: bootstrapping is finished.')

def debian7(ip,hostname):
        """Update and configure a clean Debian 7 Wheezy Machine
        """
        env.user = 'root'
        with settings(host_string='{0}'.format(ip)):

                # initial repositories
                put('files/sources.list', '/etc/apt/')
                put('files/DIR_COLORS', '/etc/')

                # update system
                run('wget http://www.dotdeb.org/dotdeb.gpg')
                run('apt-key add dotdeb.gpg')
                run('apt-get update')
                run('apt-get -y install vim-tiny')

                # temporary disable iptables
                run('apt-get -y install ufw')
                run('ufw disable')

                # set hostname
                run('echo "127.0.0.1 {0} localhost localhost.localdomain localhost4 localhost4.localdomain4" > /etc/hosts'.format(hostname))
                run('echo "::1 localhost localhost.localdomain localhost6 localhost6.localdomain6" >> /etc/hosts'.format(hostname))

                # set nameserver and search domain
                run('echo "search signs365.local" > /etc/resolv.conf')
                run('echo "nameserver 192.168.55.4" >> /etc/resolv.conf')

                # reboot
                reboot()

def xentools(ip):
        """Install xentools on a xen-based VM
        """
        env.user = 'root'
        with settings(host_string='{0}'.format(ip)):
        # test for xentools cd and install
            cd_mounted = run('dmesg | grep xvdd')
            if cd_mounted.succeeded:
            	run('mount /dev/xvdd /mnt')
                run('yum install -y /mnt/Linux/xe-guest-utilities-6.2.0-1120.i386.rpm /mnt/Linux/xe-guest-utilities-xenstore-6.2.0-1120.i386.rpm')
        print('ATTENTION: xentools installed')
