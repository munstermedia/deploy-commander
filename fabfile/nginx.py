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
    
    for project, config in get_nginx_project_config().iteritems():
        upload_template('./server/etc/nginx/site.conf',
                        config['file_path'], 
                        use_sudo=True, use_jinja=True,
                        context=config)

def get_nginx_project_config():
    if len(env.nginx) == 0:
        env.nginx = {env.project_name:{}}
    
    for project, config in env.nginx.iteritems():
        if not config.has_key('domain'):
            config['domain'] = project
            
        if not config.has_key('config_file'):
            config['config_file'] = '%s-%s.conf' % (project, env.tag)
            
        if not config.has_key('file_path'):
            config['file_path'] = '%s/%s' % (env.nginx_project_path, config['config_file'])
        
        if not config.has_key('access_log'):
            config['access_log'] = '/var/log/nginx/%s.access' % project
          
        if not config.has_key('error_log'):
            config['error_log'] = '/var/log/nginx/%s.error' % project
        
        if not config.has_key('socket'):
            config['socket'] = 'unix:///run/uwsgi/%s.sock' % project
        
        if not config.has_key('static'):
            config['static_path'] = '%s/static/' % env.source_project_tag
        
        env.nginx[project] = config
        
    return env.nginx

@task
@roles('webserver') 
def set_nginx_conf_active():
    for project, config in get_nginx_project_config().iteritems():
        enabled_path = '/etc/nginx/sites-enabled/%s-%s.conf' % (env.user, project)
        if exists(enabled_path):
            sudo('rm %s' % enabled_path)
            
        
        sudo('ln -s %s %s' % (config['file_path'], enabled_path))
    
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