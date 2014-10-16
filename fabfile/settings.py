from fabric.api import task
from fabric.api import env

from fabric.utils import abort

import json

GIT_REPO_URL = 'git@bitbucket.org:munstermedia/munstermedia.git'

APT_INSTALL = ('git',
               'libjpeg8',
               'libjpeg-dev',
               'libpng12-0',
               'libfreetype6',
               'libfreetype6-dev',
               'zlib1g',
               'libev4',
               'libev-dev',
               'python-django',
               'openssh-server',
               'openssh-client',
               'htop',
               'libmysqlclient-dev',
               'python-setuptools',
               'python-dev',
               'python-pip',
               'uwsgi',
               'libpcre3', 
               'libpcre3-dev',
               'libxml2-dev',
               'libxslt1-dev', 
               'python-dev',
               'uwsgi-plugin-python3',
               'rabbitmq-server',
               'python-celery',
               'mysql-client')



NGINX_WORKER_PROCESSES = 4
MEMCACHED_MEMORY = 64

UWSGI_LOG_PATH = '/var/log/uwsgi.log'

@task
def tag(tag):
    if not env.has_key('virtualenv_project_path'):
        abort("Run `environment:stage` first")
    # Set global tag
    env.tag = tag
    
    env.virtualenv_project_tag = '%s/%s' % (env.virtualenv_project_path, env.tag)
    env.vassals_project_ini = '%s/%s.ini' % (env.vassals_project_path, env.tag)
    env.source_project_tag = '%s/%s' % (env.source_project_path, env.tag)
    env.nginx_project_conf = '%s/%s.conf' % (env.nginx_project_path, env.tag)
    env.mysql_project_backupsql = '%s/%s.sql' % (env.mysql_project_path, env.tag)

@task
def project(project):
    if not project:
        abort("Enter project name")
    
    env.project_name = project
    env.domain = project
    env.mysql_database_name = project
    
    env.local_project_path = './../%s' % env.project_name
    
    env.nginx_error_log = '/var/log/nginx/%s.error' % env.project_name
    env.nginx_access_log = '/var/log/nginx/%s.access' % env.project_name
    env.uwsgi_error_log = '/var/log/uwsgi.log'

@task
def environment(environment):
    if environment == 'dev':
        environment = 'development'
     
    if environment == 'prod':
        environment = 'production'   
    
    default_config_file = './environments/default.json'
    try:
        with open(default_config_file) as json_file:
                default_config = json.load(json_file)
    except:
        abort("Cannot read `%s`. Is it valid json?" % default_config_file)
    
    
    env.django_settings = default_config['django_settings']
    
    
    global_config_file = './environments/%s.json' % environment
    try:
        with open(global_config_file) as json_file:
                global_config = json.load(json_file)
    except:
        abort("Cannot read `%s`. Is it valid json?" % global_config_file)
    
    
    
    env.roledefs = global_config['roledefs']
    env.password = global_config['password']
    env.user = global_config['user']
    env.db = global_config['db']
    env.env = environment
        
    
    if environment == 'dev' or environment == 'development':
        env.is_debug = 'True'
    
    if environment == 'prod' or environment == 'production':
        env.is_debug = 'False'
    
    
    # User path allways known
    env.user_path = '/home/%s' % (env.user)
    
    if env.has_key('project_name'):
        env.project_path = '/home/%s/%s' % (env.user, env.project_name)
            
        env.virtualenv_project_path = '/home/%s/virtualenv/%s' % (env.user, env.project_name)
        env.vassals_project_path = '/home/%s/vassals/%s' % (env.user, env.project_name)
        env.source_project_path = '/home/%s/source/%s' % (env.user, env.project_name)
        env.nginx_project_path = '/home/%s/nginx/%s' % (env.user, env.project_name)
        env.mysql_project_path = '/home/%s/mysql/%s' % (env.user, env.project_name)
    
       
    # When dev, create dev tag 
    if environment == 'dev' or environment == 'development':
        tag('dev')
        

