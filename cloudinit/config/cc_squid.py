#################################################################################
# Author: Cristovao Cordeiro <cristovao.cordeiro@cern.ch>                       #
#                                                                               #
# Cloud Config module for Frontier-Squid.                                       #
# Documentation in:                                                             #
# https://twiki.cern.ch/twiki/bin/view/LCG/CloudInit                            #
#################################################################################

import subprocess
try:
    import cloudinit.CloudConfig as cc
except ImportError:
    import cloudinit.config as cc
except:
    print "There is something wrong with this module installation. Please verify and rerun."
    import sys
    sys.exit(0)
from urllib import urlretrieve
import os
import re

template = [
	'net_local',		# acl NET_LOCAL src
	'cache_mem',		# cache_mem
	'cache_dir_size',	# cache_dir , size in MB
	'cache_log',		# cache_log directory
	'coredump_dir',		# coredump_dir
	'cache_dir',		# cache_dir location
	'access_log', 		# access_log - either directory or 'none'
	'logfile_rotate',	# logfile_rotate
	'http_port'		# privileged port
]


def install(params):
    os.system('rpm -Uvh http://frontier.cern.ch/dist/rpms/RPMS/noarch/frontier-release-1.0-1.noarch.rpm')
    os.system('yum -y install frontier-squid; chkconfig frontier-squid on; iptables -I INPUT 3 --proto udp --dport 3401 -j ACCEPT; restorecon -R /var/cache')

def handle(_name, cfg, cloud, log, _args):
    if 'squid' not in cfg:
        return
 
    params = cfg['squid']
    if ('install' in params) and (params['install'] == True):
        install(params)
    else:
        os.system('service frontier-squid stop')

    if 'customize_url' in params:
        urlretrieve(params['customize_url'],'/etc/squid/customize.sh')
        os.system('service frontier-squid start')
        print 'Downloaded customization file. Ending squid configuration.'
        return
    if 'customize' in params:
        try:
            file = open('/etc/squid/customize.sh','r+')
        except IOError:
            print 'customize.sh was not found. Leaving squid configuration.'
            return
        lines = file.readlines()
        lines.pop(-1)
        lines.pop(-1)
        cfg_params = params['customize']
        for option in cfg_params:
            if option == template[0]:
                lines = [re.sub('.*"acl NET_LOCAL src".*','setoption("acl NET_LOCAL src", "%s")' % cfg_params[option], word) for word in lines] 
            elif option == template[1]:
                lines = [re.sub('.*"cache_mem".*','setoption("cache_mem", "%s MB")' % str(cfg_params[option]), word) for word in lines]
            elif option == template[2]:
                lines = [re.sub('.*"cache_dir", 3,.*','setoptionparameter("cache_dir", 3, "%s")' % str(cfg_params[option]), word) for word in lines]
            elif option == template[3]:
                lines.append('setoption("cache_log", "%s")\n' % cfg_params[option])
            elif option == template[4]:
                lines.append('setoption("coredump_dir", "%s")\n' % cfg_params[option])
            elif option == template[5]:
                lines.append('setoptionparameter("cache_dir", 2, "%s")\n' % cfg_params[option])
            elif option == template[6]:
                if str(cfg_params[option]) != 'none':
                    lines.append('setoptionparameter("access_log", 1, "%s")\n' % cfg_params[option])
                else:
                    lines.append('setoption("access_log", "none")\n')
            elif option == template[7]:
                lines.append('setoption("logfile_rotate", "%s"\n)' % str(cfg_params[option]))
            elif option == template[8]:
                lines.append('setoption("http_port","%s")\n' % str(cfg_params[option]))
            else:
                print 'Invalid option %s' % cfg_params[option]

        lines.append("""print\n}'\n""")
        file.seek(0)
        file.writelines(lines)        
        file.truncate()
        file.close()
    
    os.system('service frontier-squid start')
    # END---
