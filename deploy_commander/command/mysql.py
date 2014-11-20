"""" 
MYSQL Commands for deploy commander
"""
import datetime

from fabric.api import env
from fabric.operations import run
from fabric.operations import sudo
from fabric.operations import prompt
from fabric.context_managers import hide
from fabric.context_managers import shell_env
from fabric.contrib.files import exists
from fabric.colors import green
from fabric.colors import red
from fabric.context_managers import cd

from fabfile import utils

def install_server(params):
    """
    Install mysql server
    This currently works on ubuntu systems only
    """
    with shell_env(DEBIAN_FRONTEND='noninteractive'):
        sudo('apt-get -y install mysql-server')
    
def backup_db(params):
    """" 
    This command backups the database based on a backup folder
    The output dump will be a iso date formatted filename
    """
    params = utils.format_params(params)
    
    command = """
    mysqldump -h %(host)s -u %(user)s --password='%(password)s' %(database)s > %(backup_file)s
    """
    
    backup_path = params['backup_path']
    utils.ensure_path(backup_path)
    
    backup_file = "%s/%s.sql" % (backup_path,
                                 datetime.datetime.now().isoformat())
        
    # Make params
    command_params = {'user': params['user'],
                      'password': params['password'],
                      'database': params['database'],
                      'host': params['host'],
                      'backup_file':backup_file}
    
    with hide('running'):
        run(command % command_params)      
    
    print(green("Mysql backup successfully stored in `%s`" % backup_file)) 

def query(params):
    """
    Query command for executing raw queries
    """
    params = utils.format_params(params)
    
    command = """
    mysql -h %(host)s -u %(user)s --password='%(password)s' -e '%(query)s'
    """
    # Make params
    command_params = {'user': params['user'],
                      'password': params['password'],
                      'host': params['host'],
                      'query':params['query']}
    
    run(command % command_params)
    
    print(green("Mysql query `%s` successfully runned." % command_params['query']))     
    
def import_file(params):
    """
    Given the database credentials and a import file it will import into a database
    """
    
    params = utils.format_params(params)
     
    command = """
    mysql -h %(host)s -u %(user)s --password='%(password)s' %(database)s  < %(import_file)s
    """
        
    # Make params
    command_params = {'user': params['user'],
                      'password': params['password'],
                      'database': params['database'],
                      'host': params['host'],
                      'import_file':params['import_file']}
    
    run(command % command_params)
    
    print(green("Mysql file `%s` successfully imported." % command_params['import_file']))     
    
def restore_db(params):
    """
    Restore database from a backup folder. This will first list available backups, 
    and then you'll be prompted to enter the version you'll like to import
    """
    params = utils.format_params(params)
        
    command = """
    mysql -h %(host)s -u %(user)s --password='%(password)s' %(database)s  < %(backup_file)s
    """
    
    db_backup_path = params['backup_path']
    if not 'version' in params or params['version'] == '':
        with cd(db_backup_path):
            list = run('ls -1')
        
        versions = []
        
        print(green("Available backups :"))
        print("")
        
        for mysql_file in list.split('\n'):
            mysql_version = mysql_file.replace('.sql', '')
            versions.append(mysql_version)
            print("- %s" % mysql_version)
        
        print("")
        version = prompt("Enter backup version to restore :", default=versions[-1])
        print("")
        
        if version not in versions:
            print(red("Invalid backup version..."))
            print("")
            restore_db(params)
        
        params['version'] = version
    
    backup_file = "%s/%s.sql" % (db_backup_path, params['version'])
        
    # Make params
    command_params = {'user': params['user'],
                      'password': params['password'],
                      'database': params['database'],
                      'host': params['host'],
                      'backup_file':backup_file}
    

    run(command % command_params)
    
    print(green("Mysql backup `%s` successfully restored." % backup_file)) 