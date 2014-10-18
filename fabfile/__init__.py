# from fabric.api import *
# from fabric.contrib.files import append, exists, comment, contains
# from fabric.contrib.files import upload_template as orig_upload_template
# from fabric.api import env
# from fabric.operations import local, run, sudo
# from fabric.api import task
# from fabric.context_managers import shell_env
# from fabric.contrib.console import confirm
# from fabric.colors import red, green, yellow
# from fabric.utils import abort
# from fabric.operations import prompt
from fabric.api import task
from fabric.api import roles
from fabric.api import env
from fabric.api import runs_once
from fabric.api import hosts

from fabric.contrib.files import exists

from fabric.operations import sudo
from fabric.operations import local

from settings import tag
from settings import environment
from settings import project

from apt import Apt
from apt import setup_apt

from nginx import install_nginx

from uwsgi import install_uwsgi

from memcached import install_memcached

from nginx import config_nginx_project

from uwsgi import config_uwsgi_project

from app import config_app_settings
from app import deploy_app
from app import install_app

from django import django_manage

from mysql import install_mysql
from mysql import config_mysql_replicator
from mysql import set_mysql_master_info
from mysql import config_mysql_master_replication
from mysql import restart_mysql
from mysql import install_mysql_project

@task
@hosts('localhost')
def install_mysqlserver():
    local('fab environment:%s mysql.install_mysql mysql.restart_mysql' % env.env)
    
    if len(env.roledefs['mysql']['hosts']) > 1:
        local('fab environment:%s mysql.config_mysql_replicator mysql.set_mysql_master_info mysql.config_mysql_master_replication' % env.env)
    

@task
@roles('webserver')
def install_webserver():
    Apt.upgrade()
    
    setup_apt()
    # Install default webserver
    
    setup_misc()
    
    # Install nginx and config
    install_nginx()
    
    # Install uwsgi
    install_uwsgi()
    
    # Install memcached
    install_memcached()

@task
def setup_misc():
    # Needed for pip -> solr thumbnail resizing
    if not exists('/usr/lib/libjpeg.so', use_sudo=True):
        sudo('ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib')
    
    if not exists('/usr/lib/libfreetype.so', use_sudo=True):
        sudo('ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib')
        
    if not exists('/usr/lib/libz.so', use_sudo=True):
        sudo('ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib')
    
    # Yust easy setuptools
    sudo('easy_install -U setuptools')






         
