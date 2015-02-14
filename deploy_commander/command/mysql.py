"""" 
MYSQL Commands for deploy commander
"""
import datetime
import os

from fabric.api import env
from fabric.operations import run
from fabric.operations import sudo
from fabric.operations import prompt
from fabric.context_managers import hide
from fabric.context_managers import shell_env
from fabric.contrib.files import exists
from fabric.colors import green
from fabric.colors import yellow
from fabric.colors import red
from fabric.context_managers import cd
from fabric.utils import abort
from fabric.operations import get

import utils

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
    
    backup_path = os.path.dirname(params['backup_file'])
    utils.ensure_path(backup_path)
     
    # Make params
    command_params = {'user': params['user'],
                      'password': params['password'],
                      'database': params['database'],
                      'host': params['host'],
                      'backup_file':params['backup_file']}
    
    with hide('running'):
        run(command % command_params)      
    
    with cd(backup_path):
        filename = os.path.basename(params['backup_file'])
        clean_filename = os.path.splitext(filename)[0]
        tarfilename = "%s.tar.gz" % clean_filename
        run("tar czvf %s %s" % (tarfilename, filename))
        run("rm %s" % filename)
        
    full_tar_file_path = "%s/%s" % (backup_path ,tarfilename)
    print(green("Mysql backup `%s` successfully stored." % full_tar_file_path)) 
    
    if 'download_tar_to_local_file' in params:
        get(remote_path=full_tar_file_path, local_path=params['download_tar_to_local_file'])

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
     
     
    if not exists(params['import_file']):
        print(yellow("Mysql file `%s` does not exist, so no import is executed." % params['import_file']))    
    else:
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

def cleanup_db_backups(params):
    """
    Cleanup sql backup files from folder
    """
    params = utils.format_params(params)
    
    if not 'path' in params:
        abort(red("No path param set!"))
        
    if not 'max_backup_history' in params:
        params['max_backup_history'] = 5
            
    with cd(params['path']):
        folder_result = run("ls -tr1 | grep '\.tar.gz$'")
        if len(folder_result) > 0:
            files = folder_result.split('\n')
            
            current_file_count = len(files)
            print("%s backup files found..." % current_file_count)
            
            if len(files) > params['max_backup_history']:
                total_to_remove = len(files) - params['max_backup_history']
                print("Going to remove `%s` files" % total_to_remove)
                for file in files[0:total_to_remove]:
                    file_path = "%s/%s" % (params['path'], file.strip())
                    print("- %s" % file_path)
                    run("rm %s" % (file_path))
                    
            else:
                print("No sql backup files to remove... limit is set to `%s`" % params['max_backup_history'])
        else:
            print(green("No sql backup files available..."))
    
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
            list = run("ls -1 | grep '\.tar.gz$'")
        
        versions = []
        
        print(green("Available backups :"))
        print("")
        
        for mysql_file in list.split('\n'):
            mysql_version = mysql_file.replace('.tar.gz', '')
            versions.append(mysql_version)
            print("- %s" % mysql_version)
        
        print("")
        version = prompt("Enter backup version to restore :", default=versions[-1])
        print("")
        
        if version not in versions:
            print(red("Invalid backup version..."))
            print("")
            restore_db(params)
        else:
            params['version'] = version
    
    with cd(db_backup_path):
        run("tar zxvf %s.tar.gz" % params['version'])
    
    backup_file = "%s/%s.sql" % (db_backup_path, params['version'])
        
    # Make params
    command_params = {'user': params['user'],
                      'password': params['password'],
                      'database': params['database'],
                      'host': params['host'],
                      'backup_file':backup_file}
    

    run(command % command_params)
    
    print(green("Mysql backup `%s` successfully restored." % backup_file))
    
    run("rm %s" % backup_file)