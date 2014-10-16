import os.path
import os

from fabric.api import task
from fabric.api import env
from fabric.api import roles

from fabric.contrib.files import exists

from fabric.operations import sudo
from fabric.operations import run
from fabric.operations import prompt

from fabric.utils import abort

from fabric.colors import red
from fabric.colors import yellow

from fabric.utils import abort

from fabric.contrib.console import confirm

from utils import upload_template
from utils import ensure_path

from memcached import restart_memcached

from uwsgi import config_uwsgi_project
from uwsgi import set_uwsgi_ini_active
from uwsgi import restart_uwsgi
from uwsgi import ensure_uwsgi_socket_path

from nginx import config_nginx_project
from nginx import set_nginx_conf_active
from nginx import restart_nginx

from pip import setup_pip_project

from mysql import setup_mysql_dev
from mysql import backup_database

from django import django_manage

from settings import GIT_REPO_URL


@task
@roles('webserver')
def install_app():
    if not env.has_key('project_name'):
        abort('No project known, execute with `fab project:name install_app` first')
    
    if env.env == 'production':
        repo_path = '/home/%s/repo/%s' % (env.user, env.project_name)
        
        # Ensure path exists
        ensure_path('/home/%s/repo' % (env.user))
        
        key_name = '%s_rsa' % env.project_name
        
        if not exists(repo_path):
            #run('chmod -R 777 ~/.ssh')
            
            if confirm("Create new key?"):
                run('ssh-keygen -t rsa -b 2048 -f ~/.ssh/%s -N \'\'' % (key_name))
            
            #sudo('chmod -R 600 ~/.ssh')
            
            #sudo('chmod 600 ~/.ssh/%s' % key_name)
            
            
            #sudo('chmod 644 ~/.ssh/known_hosts')
            
            upload_template('./server/ssh/config', '~/.ssh/config',
                            use_sudo=True, use_jinja=True,
                            context={'KEY_NAME': key_name})
            
            print(yellow("Add this key to github or bitbucket or something..."))
            run('cat .ssh/%s.pub' % key_name)
            
            if confirm("Done adding the key, can we checkout the repo ?"):
                run('git clone %s %s' % (GIT_REPO_URL, repo_path))
            else:
                abort(red("Cancelled you'll need to be ready with the key!"))
    
        ensure_path(env.virtualenv_project_path)
        ensure_path(env.vassals_project_path)
        ensure_path(env.source_project_path)
        ensure_path(env.nginx_project_path)
        ensure_path(env.mysql_project_path)
    
    if env.env == 'development':
        # Ensure source project path
        ensure_path(env.source_project_path)
        
        # Create symlink to generic folder structure 
        if exists(env.source_project_tag):
            sudo('rm %s' % env.source_project_tag)
            
        sudo('ln -s /project/%s %s' % (env.project_name, env.source_project_tag))
        
        # Import mysql database
        setup_mysql_dev()
        
        # Prepare virtualenv
        setup_pip_project()
        
        # Create nginx file
        config_nginx_project()

        # Create symlink to active conf
        set_nginx_conf_active()
        
        # Create uwsgi vassal
        config_uwsgi_project()
    
        
        
        # Restart uwsgi just to be sure
        restart_uwsgi()
        
        # Restart nginx to add the new conf
        restart_nginx()
        
        # Sync the project
        django_manage('migrate')
      
@task
@roles('webserver')
def rollback_app():  
    if env.env == 'development':
        abort(red("Rollback on development? :)"))

    if not env.tag:
        abort("Run `tag:<tagname>` first")

    # Create symlink to active conf
    set_nginx_conf_active()
    
    # Set active uwsgi
    set_uwsgi_ini_active()
    
    # Restart uwsgi just to be sure
    restart_uwsgi()
        
    # Restart nginx to add the new conf
    restart_nginx()
    
    # Make sure memcached is empty
    restart_memcached()

@task
@roles('webserver')
def deploy_app():
    if env.env == 'development':
        abort(red("Deploy on development? :)"))
    
    if not env.tag:
        abort("Run `tag:<tagname>` first")
    
    
    tag = env.tag
    
    if len(tag) == 0:
        abort(red("Invalid tag"))
    
    ensure_path(env.virtualenv_project_path)
    ensure_path(env.vassals_project_path)
    ensure_path(env.source_project_path)
    ensure_path(env.nginx_project_path)
    ensure_path(env.mysql_project_path)
    
    # Dump the current database
    backup_database()
    
    # Make repo path
    repo_path = '/home/%s/repo/%s' % (env.user, env.project_name)
    
    # Update local repo with latest code
    run('git --git-dir="%s/.git" --work-tree="%s/." pull origin %s' % (repo_path, repo_path, env.tag))
    
    # If exist remove full source
    if exists(env.source_project_tag):
        run('rm -Rf %s' % env.source_project_tag)
    
    # Copy source code to version
    run('cp -R %s %s' % (repo_path, env.source_project_tag))
    
    # Copy default local settings
    config_app_settings()

    # Generate /run/uwsgi path if not existing (might not exist on reboot)
    ensure_uwsgi_socket_path()
    
    # Prepare virtualenv
    setup_pip_project()
    
    # Create nginx file
    config_nginx_project()
    
    # Create symlink to active conf
    set_nginx_conf_active()
        
    # Create uwsgi vassal
    config_uwsgi_project()
    
    # Set active uwsgi
    set_uwsgi_ini_active()
    
    # Restart uwsgi just to be sure
    restart_uwsgi()
        
    # Restart nginx to add the new conf
    restart_nginx()
    
    # Make sure memcached is empty
    restart_memcached()
    
@task   
@roles('webserver')     
def config_app_settings():
    print("Task : %s, Executing on %s as %s" % ('setup_django_config', env.host, env.user))
    upload_template('./server/django/settings/local.deploy',
                    '%s/%s/settings/local.py' % (env.source_project_tag, env.project_name),
                    use_sudo=True, use_jinja=True,
                    context=env.django_settings)