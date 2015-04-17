from fabric.api import *
import os, time, logging, re, sys
from pprint import *

# uncomment for debugging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
# pprint(locals())

epoch_time = int(time.time())

def install(ip):
        """Install Jetbrains Youtrack on a centos 6 box
        """
        env.user = 'root'
        with settings(host_string='{0}'.format(ip)):
		# backups
		run('yum install -y cifs-utils')
		run('echo "//services01/backupstore /mnt/services01 cifs user,username=backupuser,password=XC801C!bash,rw,nounix,noserverino,iocharset=utf8,file_mode=0666,dir_mode=0777 0 0" >> /etc/fstab')
		run('mkdir /mnt/services01')
		run('mount /mnt/services01')

		run('yum install -y java-1.7.0-openjdk')
		run('http://download.jetbrains.com/charisma/youtrack-6.0.12634.jar')
		run('java -Xmx1g -XX:MaxPermSize=250m -Djava.awt.headless=true -jar youtrack-6.0.12634.jar 80')
