from fabric.api import *
import os, time, logging, re, sys
from pprint import *

# uncomment for debugging
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)
#pprint(locals())

epoch_time = int(time.time())

def install(ip,hostname):

        """Update and configure a clean DEBIAN7 machine as signs365 webserver (server01)
        """

        env.user = 'root'
        with settings (
			host_string='{0}'.format(ip),
			warn_only=True
		):
		
		# update system and install all packages
		dotdeb_installed = run('apt-key list|grep dotdeb')
		if not dotdeb_installed:
			run('wget http://www.dotdeb.org/dotdeb.gpg')
			run('apt-key add dotdeb.gpg')

		run('apt-get install -y dselect')
		run('apt-get update')
		run('aptitude install -y $(cat /root/package.list | awk \'{print $1}\')')

		# Get all files pushed to client
		put('files/server01/sources.list', '/etc/apt/sources.list')
		put('files/server01/apache2.conf.tar.gz', '/etc/apache2/apache2.conf.tar.gz')
		put('files/server01/package.list', '/root/package.list')
		put('files/server01/gearmand-1.1.12.tar.gz', '/root/gearmand-1.1.12.tar.gz')
		put('files/server01/supervisor.conf.tar.gz', '/etc/supervisor/conf.d/supervisor.conf.tar.gz')
		put('files/server01/php5.tar.gz', '/etc/php5/php5.tar.gz')

		# uncompress custom configuration
		config_present = run('ls /etc/apache2/apache2.conf.tar.gz')
		if not config_present:
			run('cd /etc/apache2; tar zxvf apache2.conf.tar.gz')
	
		config_present = run('ls /etc/php5/php5.tar.gz')
		if not config_present:
			run('cd /etc/php5; tar zxvf php5.tar.gz')	

		config_present = run('ls /etc/supervisor/conf.d/supervisor.conf.tar.gz')
		if not config_present:
			run('cd /etc/supervisor/conf.d/; tar zxvf supervisor.conf.tar.gz')

		# install and configure gearman 1.1.12
		gearman_installed = run('gearadmin --help')
		if not gearman_installed:
			run('cd /root; tar zxvf gearmand-1.1.12.tar.gz; cd gearmand-1.1.12; ./configure && make && make install')
		
		# users
		users = ['wmacomber','szornes','webuser','chatbot','gearman','logging']
		for x in users:
			user_created = run('cat /etc/passwd|grep {0}'.format(x))
			if not user_created:
				run('useradd {0}'.format(x))
				run('mkdir -p /home/{0}/.ssh'.format(x))
				run('cp /etc/skel/.* /home/{0}/'.format(x))
				put('files/server01/{0}_authorized_keys'.format(x), '/home/{0}/.ssh/authorized_keys'.format(x))
				run('chown -R {0}:{0} /home/{0}'.format(x))

		users = ['wmacomber','szornes']
		for x in users:
			sudo_created = run('cat /etc/sudoers|grep {0}'.format(x))
			if not sudo_created:
				run('echo \'{0} ALL=(ALL) NOPASSWD:ALL\' >> /etc/sudoers'.format(x))

