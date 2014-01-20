#/usr/bin/python

import os
import pwd
import socket
import subprocess
import multiprocessing

template = {
        
	# Defaults
	'DAEMON_LIST' : 'MASTER, STARTD',
	'HIGHPORT' : '24500',
	'LOWPORT' : '20000',
	'START' : 'TRUE',
	'SUSPEND' : 'FALSE',
	'PREEMPT' : 'FALSE',
	'KILL' : 'FALSE',
	'QUEUE_SUPER_USERS' : 'root, condor',
	'ALLOW_WRITE' : 'condor@*.*',
	'STARTER_ALLOW_RUNAS_OWNER' : 'False',
	'ALLOW_DAEMON' : 'voatlas217.cern.ch',
	'HOSTALLOW_DAEMON' : 'voatlas217.cern.ch',
	'SEC_DEFAULT_AUTHENTICATION' : 'REQUIRED',
	'SEC_DEFAULT_AUTHENTICATION_METHODS' : 'PASSWORD',
	'SEC_PASSWORD_FILE' : '/root/pool_password',
	'JAVA' : '/usr/lib/jvm/java-1.6.0-openjdk-1.6.0.0.x86_64/jre/bin/java',
	'RELEASE_DIR' : '/usr',
	'LOCAL_DIR' : '/var',
	'RANK' : '0',
	
	# Contex
	'UID_DOMAIN' : None,
        'GSITE' : None,
        
	# ATLAS
	'CONDOR_HOST' : 'voatlas217.cern.ch',
	'COLLECTOR_HOST' : 'voatlas217.cern.ch:20618',
	'CONDOR_ADMIN' : 'root@voatlas217.cern.ch:20618',
	'DEDICATED_EXECUTE_ACCOUNT_REGEXP' : 'atlcloud',
	'USER_JOB_WRAPPER' : '/usr/local/bin/lcg-atlas',
	'STARTD_ATTRS' : 'GSITE',
	'ENABLE_SSH_TO_JOB' : 'True',
	'CERTIFICATE_MAPFILE' : '/etc/condor/canonical_map',
	'EXECUTE' : '/scratch/condor',
	'STARTER_DEBUG' : 'D_FULLDEBUG',
	'STARTD_DEBUG' : 'D_FULLDEBUG',
	'UPDATE_COLLECTOR_WITH_TCP' : 'True',
	'MAXJOBRETIREMENTTIME' : '48*3600',
	'STARTD_CRON_JOBLIST' : '$(STARTD_CRON_JOBLIST) atlval',
	'STARTD_CRON_ATLVAL_MODE' : 'Periodic',
	'STARTD_CRON_ATLVAL_EXECUTABLE' : '/usr/libexec/atlval.sh',
	'STARTD_CRON_ATLVAL_PERIOD' : '60s',
	'STARTD_CRON_ATLVAL_JOB_LOAD' : '0.1',
        'SLOT1_USER' : 'cuser1' 
}

def handle(_name, cfg, cloud, log, _args):
    if not 'condor' in cfg:
        return
    else:
        condor_cc_cfg = cfg['condor']   
	
    # Add user provided values
    for parameter in condor_cc_cfg:
        if parameter in template:
            template[parameter] = condor_cc_cfg[parameter]

    # Add discoverable values
    ip_addr = socket.gethostbyname(socket.getfqdn())
    template['FILESYSTEM_DOMAIN'] = ip_addr	
    template['HOSTALLOW_DAEMON'] +=  ", %s" % (ip_addr)
    template['ALLOW_DAEMON'] += ", %s,  127.0.0.1" % (ip_addr)
	
    # Add dynamically discovered SLOT users
    condor_uid = pwd.getpwnam('condor').pw_uid
    condor_gid = pwd.getpwnam('condor').pw_gid
    template['CONDOR_ID'] = "%s.%s" % (condor_uid, condor_gid)
    if 'SLOT_USER' in  condor_cc_cfg and str(condor_cc_cfg['SLOT_USER']) == 'True':
        for count in range(1, multiprocessing.cpu_count() + 1):
            template["SLOT%s_USER" % (count)] = "cuser%s" % (count)
            os.system("/usr/sbin/useradd -m -s /sbin/nologin  cuser%s > /dev/null 2>&1\n" % (count))
    else:
        os.system("/usr/sbin/useradd -m -s /sbin/nologin  cuser1 > /dev/null 2>&1\n")
    # Create configuration file
    condor_config_file = '/etc/condor/condor_config.local'
    #condor_config_file = 'condor_config.local'
    file_handle = open(condor_config_file,'w') 
    for parameter in template:
        file_handle.write("%s = %s\n" %(parameter, template[parameter]))
    file_handle.close()
	
    # Restart  condor
    subprocess.check_call(['/sbin/service', 'condor', 'restart'])

if __name__ == "__main__":
	
    config = {
        'condor' : {		},
    }
    
    handle(None, config, None, None, None)
	

