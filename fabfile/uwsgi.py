from fabric.api import task
from fabric.api import env
from fabric.api import roles

from fabric.operations import sudo

from fabric.contrib.files import exists

from fabric.utils import abort

from utils import upload_template
from utils import ensure_path

from settings import UWSGI_LOG_PATH

@task
def install_uwsgi():
    # Install main uwsgi
    sudo('sudo pip install uwsgi')
    
    # Generate /run/uwsgi path
    ensure_uwsgi_socket_path()
    
    # Create vassals path
    if not exists('/etc/uwsgi/vassals/'):
        sudo('mkdir /etc/uwsgi/vassals/')
    
    # Upload config
    upload_template('./server/etc/init/uwsgi.conf', '/etc/init/uwsgi.conf',
                    use_sudo=True, use_jinja=True,
                    context={'UWSGI_LOG_PATH': UWSGI_LOG_PATH})

@task 
def ensure_uwsgi_socket_path():
    # Create tmp path for sockets
    if not exists('/run/uwsgi'):
        sudo('mkdir /run/uwsgi')
    
    # Make sure it's writable
    sudo('/bin/chmod 0777 -R /run/uwsgi')

@task
def config_uwsgi_project():
    if not env.tag:
        abort("No tag set")
    
    ensure_path(env.vassals_project_path)
     
    upload_template('./server/etc/uwsgi/vassals/uwsgi.ini',
                    env.vassals_project_ini, 
                    use_sudo=True, use_jinja=True, 
                    context={'PROJECT_NAME': env.project_name,
                             'USER': env.user,
                             'SOURCE_PROJECT_TAG': env.source_project_tag,
                             'VIRTUALENV_PROJECT_TAG': env.virtualenv_project_tag })
    
@task
@roles('webserver') 
def set_uwsgi_ini_active():
    ini_path = '/etc/uwsgi/vassals/%s.ini' % env.project_name
    if exists(ini_path):
        sudo('rm %s' % ini_path)
    
    sudo('ln -s %s %s' % (env.vassals_project_ini, ini_path))
    
@task
@roles('webserver') 
def restart_uwsgi():
    sudo('service uwsgi restart')
    sudo('touch /etc/uwsgi/vassals/*')
    
@task
@roles('webserver') 
def tail_uwsgi_error_log():
    sudo('tail -f %s' % env.uwsgi_error_log)
    
    