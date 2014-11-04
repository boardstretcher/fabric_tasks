from fabric.api import *
import os, time, logging, re, sys
from pprint import *

# uncomment for debugging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
# pprint(locals())

epoch_time = int(time.time())

def bootstrap(ip,hostname):
        """Update and configure a clean Centos 6.6 VM for FreePBX
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
                run('yum install -y gcc gcc-c++ lynx bison mysql-devel mysql-server php php-xml php-mysql php-pear php-mbstring tftp-server httpd make ncurses-devel libtermcap-devel sendmail sendmail-cf caching-nameserver sox newt-devel libxml2-devel libtiff-devel audiofile-devel gtk2-devel subversion kernel-devel git subversion kernel-devel php-process crontabs cronie cronie-anacron doxygen sqlite-devel vim wget speex-devel gsm-devel libuuid-devel')
                #run('rm -f /etc/yum.repos.d/*')

                # custom colors and history format
                run('sed -i "s/DIR\ 01\;34/DIR\ 40\;33/g" /etc/DIR_COLORS ')

                # temporary disable iptables
                run('service iptables stop')
                run('chkconfig iptables off')

                # enable mysql, apache
                run('chkconfig --level 345 mysqld on; chkconfig --level 345 httpd on;')
                run('service mysqld start; service httpd start;')

                # install peardb
                run('pear channel-update pear.php.net')
                run('pear install db')

                # set hostname
                run('echo "127.0.0.1 {0} localhost localhost.localdomain localhost4 localhost4.localdomain4" > /etc/hosts'.format(hostname))
                run('echo "::1 localhost localhost.localdomain localhost6 localhost6.localdomain6" >> /etc/hosts'.format(hostname))
                run('sed -i "s/HOSTNAME=localhost.localdomain/HOSTNAME={0}/g" /etc/sysconfig/network'.format(hostname))

                # set nameserver and search domain
                # run('echo "search yournetwork.local" > /etc/resolv.conf')
                # run('echo "nameserver yournameserver.local" >> /etc/resolv.conf')

                # test for xentools cd and install
                cd_mounted = run('dmesg | grep xvdd')
                if cd_mounted.succeeded:
                        run('mount /dev/xvdd /mnt')
                        run('yum install -y /mnt/Linux/xe-guest-utilities-6.2.0-1120.i386.rpm /mnt/Linux/xe-guest-utilities-xenstore-6.2.0-1120.i386.rpm')

                # reboot
                reboot()
                print('ATTENTION: bootstrapping is finished. You may now run the install function.')
                print('**************')
                print('WARNING: iptables and selinux have been disabled, please configure them to suit your environment')
                print('and re-enable them.')

def install(ip):
        """Install asterisk 12 and FreePBX on the Centos 6.6 VM
        """
        env.user = 'root'
        with settings(host_string='{0}'.format(ip)):
                # asterisk and its dependencies
                run('wget http://srtp.sourceforge.net/srtp-1.4.2.tgz')
                run('tar zxvf srtp-1.4.2.tgz')
                with cd('/root/srtp'):
                        run('autoconf')
                        run('./configure')
                        run('sed -i "s/CFLAGS.= -Wall/CFLAGS = -fPIC -Wall/g" Makefile')
                        run('make; make install; cp /usr/local/lib/libsrtp.a /lib')

                run('git clone https://github.com/asterisk/pjproject pjproject')
                with cd('/root/pjproject/'):
                        run('./configure --prefix=/usr --enable-shared --disable-sound --disable-resample --disable-video --disable-opencore-amr --with-external-speex --with-external-srtp --with-external-gsm --libdir=/usr/lib64')
                        run('make dep; make; make install;')

                run('wget http://www.digip.org/jansson/releases/jansson-2.5.tar.gz')
                run('tar zxvf jansson-2.5.tar.gz')
                with cd('/root/jansson-2.5'):
                        run('./configure --prefix=/usr/')
                        run('make; make install;')
                        run('ldconfig')

                run('wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-12-current.tar.gz')
                run('tar xf asterisk-12-current.tar.gz')
                with cd('asterisk-12*'):
                        run('./configure')
                        run('make; make install;')

                run('yum install -y asterisk-sounds*')

                with shell_env(VER_FREEPBX='12.0'):
                        with cd('/usr/src'):
                                run('git clone http://git.freepbx.org/scm/freepbx/framework.git freepbx')
                        with cd('/usr/src/freepbx'):
                                run('git checkout release/${VER_FREEPBX}')

                run('adduser asterisk -M -c "Asterisk User"')
                run('touch /var/run/asterisk/asterisk.pid')
                run('chown -R asterisk. /var/run/asterisk')
                run('chown -R asterisk. /etc/asterisk')
                run('chown -R asterisk. /var/{lib,log,spool}/asterisk')
                run('chown -R asterisk. /usr/lib/asterisk')
                run('chown -R asterisk. /var/www/')
                run('sed -i "s/\(^upload_max_filesize = \).*/\\120M/" /etc/php.ini')
                run('cp /etc/httpd/conf/httpd.conf /etc/httpd/conf/httpd.conf_orig')
                run('sed -i "s/^\(User\|Group\).*/\\1 asterisk/" /etc/httpd/conf/httpd.conf')
                run('sed -i "s/AllowOverride None/AllowOverride All/g" /etc/httpd/conf/httpd.conf')
                run('service httpd restart')
                run('ldconfig')

                with shell_env(ASTERISK_DB_PW='amp109'):
                        with cd('/usr/src/freepbx'):
                                run('mysqladmin -u root create asterisk')
                                run('mysqladmin -u root create asteriskcdrdb')
                                run('mysql -u root asterisk < SQL/newinstall.sql')
                                run('mysql -u root asteriskcdrdb < SQL/cdr_mysql_table.sql')
                                run('mysql -u root -e "GRANT ALL PRIVILEGES ON asterisk.* TO asteriskuser@localhost IDENTIFIED BY \'${ASTERISK_DB_PW}\';"')
                                run('mysql -u root -e "GRANT ALL PRIVILEGES ON asteriskcdrdb.* TO asteriskuser@localhost IDENTIFIED BY \'${ASTERISK_DB_PW}\';"')
                                run('mysql -u root -e "flush privileges;"')

                        with cd('/usr/src/freepbx'):
                                run('./start_asterisk start')
                                run('./install_amp --dbname asterisk --username asteriskuser --password ${ASTERISK_DB_PW}')
                                run('amportal a ma download manager')
                                run('amportal a ma install manager')
                                run('amportal a ma download userman')
                                run('amportal a ma install userman')
                                run('amportal a ma download sipstation')
                                run('amportal a ma install sipstation')
                                run('amportal a ma installall')
                                run('amportal chown')
                                run('amportal a reload')

                                run('ln -s /var/lib/asterisk/moh /var/lib/asterisk/mohmp3')
                                run('service httpd restart')
                                run('amportal start')
