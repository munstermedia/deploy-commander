import utils
import time

from fabric.api import task
from fabric.api import env
from fabric.api import roles
from fabric.api import runs_once
from fabric.api import hosts

from fabric.operations import local
from fabric.operations import sudo
from fabric.operations import run
from fabric.operations import put

from fabric.colors import red
from fabric.colors import yellow
from fabric.context_managers import shell_env

from fabric.utils import abort
from fabric.contrib.files import exists



@task
@runs_once
@roles('webserver')
def backup():
    utils.init_env_settings('webserver')
    
    command = """
    mysqldump -h %(host)s -u %(user)s --password='%(password)s' %(database)s > %(backup_file)s
    """
    
    settings = env.mysql_backup["db"]
    
    # Make params for db backup path
    url_params = {'project_folder':env.project_folder,
                  'user':env.user,
                  'tag':env.tag,
                  'domain':env.site['domain']}
    
    db_backup_path = env.mysql_backup['db_backup_path'] % url_params
    utils.ensure_path(db_backup_path)
    
    backup_file = "%s/%s.sql" % (db_backup_path, env.tag)
    
    if exists(backup_file):
        target_file = "%s/%s-%s.sql" % (db_backup_path, env.tag, time.time())
        print(yellow("Backup sql `%s` exists.. it will be renamed to `%s`" % (backup_file, target_file)))
        run('mv %s %s' % (backup_file, target_file))
        
    # Make params
    command_params = {'user':settings['user'],
                      'password':settings['password'],
                      'database':settings['database'],
                      'host':settings['host'],
                      'backup_file':backup_file}
    
    run(command % command_params)

@task
@runs_once
@roles('webserver')
def restore():
    utils.init_env_settings('webserver')
    
    command = """
    mysql -h %(host) -u %(user)s --password='%(password)s' %(database)s < %(backup_file)s
    """
    
    settings = env.mysql_backup["db"]
    
    # Make params for db backup path
    url_params = {'project_folder':env.project_folder,
                  'user':env.user,
                  'tag':env.tag,
                  'domain':env.site['domain']}
    
    db_backup_path = env.mysql_backup['db_backup_path'] % url_params
    
    backup_file = "%s/%s.sql" % (db_backup_path, env.tag)
    
    # Make params
    command_params = {'user':settings['user'],
                      'password':settings['password'],
                      'database':settings['database'],
                      'host':settings['host'],
                      'backup_file':backup_file}
    
   
    run(command % (env.mysql_database_name, env.mysql_project_backupsql))
     
