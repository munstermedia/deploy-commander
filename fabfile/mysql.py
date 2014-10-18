from apt import Apt

from fabric.api import task
from fabric.api import env
from fabric.api import roles
from fabric.api import runs_once


from fabric.operations import sudo
from fabric.operations import run
from fabric.operations import put

from fabric.colors import red
from fabric.context_managers import shell_env

from fabric.utils import abort

from utils import upload_template
 



@task
@roles('mysql')
def install_mysql():
    with shell_env(DEBIAN_FRONTEND='noninteractive'):
        Apt.install('mysql-server')
    
    command = """mysqladmin -u root -p password '%s'"""
    sudo(command % env.roledefs['mysql']['config'][env.host]['root_password'])
    
    upload_template( './server/etc/mysql/my.cnf', '/etc/mysql/my.cnf', 
            use_sudo=True, use_jinja=True, context={
        'MYSQL_SERVER_ID': env.roledefs['mysql']['config'][env.host]['server_id'],
        'MYSQL_BIND_ADDRESS' : env.roledefs['mysql']['config'][env.host]['ip'], 
        'MYSQL_AUTO_INCREMENT_OFFSET' : env.roledefs['mysql']['config'][env.host]['server_id'],
        'MYSQL_AUTO_INCREMENT' : len(env.roledefs['mysql']['config'])
    })

@task
@runs_once
def install_mysql_project():
    put('%s/.data/mysql/install.sql' % env.local_project_path, './tmp_sql.sql')
    command = """ 
    mysql --user="root" --password='%s' -e "CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET \'utf8\';"
    """
    sudo(command % (env.roledefs['mysql']['config'][env.host]['root_password'], env.mysql_database_name))
    
    command = """
    mysql -u root --password='%s' %s < ./tmp_sql.sql
    """
    sudo(command % (env.roledefs['mysql']['config'][env.host]['root_password'], env.mysql_database_name))
    run('rm ./tmp_sql.sql')


@task
@runs_once
def backup_database():
    root_password = env.roledefs['mysql']['config'][env.host]['root_password']
    command = """
    mysqldump -u root --password='%s' %s > %s
    """
    sudo(command % (root_password, env.mysql_database_name, env.mysql_project_backupsql))

@task
@runs_once
def restore_database():
    root_password = env.roledefs['mysql']['config'][env.host]['root_password']
    command = """
    mysql -u root --password='%s' %s %s < %s
    """
    sudo(command % (env.mysql_database_name, env.mysql_project_backupsql))

@task
@roles('mysql')
def config_mysql_replicator():
    try:
        root_password = env.roledefs['mysql']['config'][env.host]['root_password']
        command = """
        mysql -u root --password='%s' -e "create user 'replicator'@'%%' identified by '%s'"
        """
        sudo(command % (root_password, env.roledefs['mysql']['config'][env.host]['replicator_password'])); 
        
        command = """
        mysql -u root --password='%s' %s -e "grant replication slave on *.* to 'replicator'@'%'";
        """
        sudo(command % (root_password))
    except:
        print(red("Cannot create user replicator... maybe it's allready setup?"))

@task
@roles('mysql')
def config_mysql_master_replication():
    print "Processing env %s" % env.host
    other_master_ip = env.roledefs['mysql']['config'][env.host]['master_file_server']
    
    if not 'master_file' in env.roledefs['mysql']['config'][other_master_ip]:
        abort(red("Run with set_mysql_master_info first!"))
        
    other_master = env.roledefs['mysql']['config'][other_master_ip]
    
    command = """mysql -u root --password='%s' -e "slave stop;" """
    sudo(command % env.roledefs['mysql']['config'][env.host]['root_password'])
    
    command ="""
    mysql -u root --password='%s' -e "
    CHANGE MASTER TO MASTER_HOST = '%s', 
    MASTER_USER = 'replicator', 
    MASTER_PASSWORD = '%s',
    MASTER_LOG_FILE = '%s',
    MASTER_LOG_POS = %s;" """
    sudo(command % (
                    env.roledefs['mysql']['config'][env.host]['root_password'],
                    other_master_ip, 
                    other_master['replicator_password'],
                    other_master['master_file'],
                    other_master['master_position']
                    ))  
    
    command = """mysql -u root --password='%s' -e "slave start;" """
    sudo(command % env.roledefs['mysql']['config'][env.host]['root_password']);

@task
@roles('mysql')
def set_mysql_master_info():
    print "Retrieve MASTER info from  `%s`" % env.host
    command = """mysql -u root --password='%s' --skip-column-names -A -e "SHOW MASTER STATUS;" | awk '{print $1}'"""
    env.roledefs['mysql']['config'][env.host]['master_file'] = sudo(command % (env.roledefs['mysql']['config'][env.host]['root_password']))
    print "Master file : %s" % env.roledefs['mysql']['config'][env.host]['master_file']
    
    command = """mysql -u root --password='%s' --skip-column-names -A -e "SHOW MASTER STATUS;" | awk '{print $2}'"""
    env.roledefs['mysql']['config'][env.host]['master_position'] = sudo(command % (env.roledefs['mysql']['config'][env.host]['root_password']))
    print "Master position : %s" % env.roledefs['mysql']['config'][env.host]['master_position']
    
@task
@roles('mysql')
def restart_mysql():
    sudo('service mysql restart')
     
