import os.path
import os
import fabfile.utils
import pprint
import mysql
import datetime

from fabric.api import task
from fabric.api import env
from fabric.api import roles

from fabric.contrib.files import exists
from fabric.contrib.files import is_link

from fabric.operations import sudo
from fabric.operations import run
from fabric.operations import prompt

from fabric.utils import abort

from fabric.colors import red
from fabric.colors import yellow
from fabric.colors import green

from fabric.utils import abort

from fabric.operations import prompt
from fabric.contrib.console import confirm

from fabric.context_managers import cd

from fabfile import utils
from fabric.utils import abort

from fabric.context_managers import hide

def backup_db(params):
    command = """
    mysqldump -h %(host)s -u %(user)s --password='%(password)s' %(database)s > %(backup_file)s
    """
    
    backup_path = params['backup_path'] % env.params
    utils.ensure_path(backup_path)
    
    backup_file = "%s/%s.sql" % (backup_path,
                                 datetime.datetime.now().isoformat())
        
    # Make params
    command_params = {'user': params['user'] % env.params,
                      'password': params['password'] % env.params,
                      'database': params['database'] % env.params,
                      'host': params['host'] % env.params,
                      'backup_file':backup_file}
    
    with hide('running', 'stdout', 'stderr'):
        run(command % command_params)      
    
    print(green("Mysql backup successfully stored in `%s`" % backup_file)) 
    
def restore_db(params):
    command = """
    mysql -h %(host)s -u %(user)s --password='%(password)s' %(database)s  < %(backup_file)s
    """
    
    db_backup_path = params['backup_path'] % env.params
    if not 'version' in params:
        run('ls -las %s' % db_backup_path)
        params['version'] = prompt("Enter backup version to restore :")
    
    backup_file = "%s/%s.sql" % (db_backup_path, params['version'])
        
    if not exists(backup_file):
        print(red("Invalid backup version..."))
        del params['version']
        restore_db(params)
    
        
    # Make params
    command_params = {'user': params['user'] % env.params,
                      'password': params['password'] % env.params,
                      'database': params['database'] % env.params,
                      'host': params['host'] % env.params,
                      'backup_file':backup_file}
    
    with hide('running', 'stdout', 'stderr'):
        run(command % command_params)
    
    print(green("Mysql backup `%s` successfully restored." % backup_file)) 