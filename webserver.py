from fabric.api import *
import os, time, logging, re, sys
from pprint import *

# uncomment for debugging
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)
#pprint(locals())

epoch_time = int(time.time())

def install(ip,hostname):
        """Update and configure a clean machine with webserver requirements
        """
        env.user = 'root'
        with settings(host_string='{0}'.format(ip)):
		put('sources.list', '/etc/apt/sources.list')
		run('apt-get install -y dselect')
		run('apt-get update')
		put('package.list', '/root/package.list')
                run('aptitude install -y $(cat /root/package.list | awk \'{print $1}\')')


