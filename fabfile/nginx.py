from apt import Apt

from fabric.api import task
from fabric.api import env
from fabric.api import roles

from fabric.contrib.files import exists

from fabric.operations import sudo

from utils import upload_template
from utils import ensure_path

from settings import NGINX_WORKER_PROCESSES

@task
@roles('webserver')     
def install_nginx():
    # Run apt-get install nginx
    Apt.install('nginx')
    
    # Copy template nginx config
    upload_template('/server/etc/nginx/nginx.conf', '/etc/nginx/nginx.conf', 
                    use_sudo=True, use_jinja=True, 
                    context={'NGINX_WORKER_PROCESSES': NGINX_WORKER_PROCESSES})
    
    # Check default hosts, and delete if there
    assert exists('/etc/nginx/sites-enabled') # Right package install format?
    if exists('/etc/nginx/sites-enabled/default'):
        sudo('rm /etc/nginx/sites-enabled/default')

@task
@roles('webserver') 
def config_nginx_project():
    print("Task : %s, Executing on %s as %s" % ('configure_nginx', env.host, env.user))
    
    ensure_path(env.nginx_project_path)
    
    upload_template('./server/etc/nginx/site.conf',
                    env.nginx_project_conf, 
                    use_sudo=True, use_jinja=True,
                    context={'PROJECT_NAME': env.project_name,
                             'USER': env.user,
                             'SOURCE_PROJECT_TAG':env.source_project_tag,
                             'DOMAIN': env.domain})

@task
@roles('webserver') 
def set_nginx_conf_active():
    enabled_path = '/etc/nginx/sites-enabled/%s.conf' % env.project_name
    if exists(enabled_path):
        sudo('rm %s' % enabled_path)
        
    
    sudo('ln -s %s %s' % (env.nginx_project_conf, enabled_path))
    
@task
@roles('webserver') 
def restart_nginx():
    sudo('service nginx restart')


@task
@roles('webserver') 
def tail_nginx_error_log():
    sudo('tail -f %s' % env.nginx_error_log)
    
    
@task
@roles('webserver') 
def tail_nginx_access_log():
    sudo('tail -f %s' % env.nginx_access_log)