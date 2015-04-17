from fabric.api import *
import os, time, logging, re, sys
from pprint import *

# uncomment for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
pprint(locals())

epoch_time = int(time.time())

def nagios():
        """Run a backup of the nagios/adagios system
        """
        env.user = 'root'
        with settings(host_string='192.168.192.51'):

                # set nameserver and search domain
                run('$(which rsync) -varh -O -L --progress --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/mnt/*","/media/*","/lost+found"} /* /mnt/services01/nagios/')
