from apt import Apt

from fabric.api import task
from fabric.api import env
from fabric.api import roles

from fabric.colors import green

from fabric.operations import sudo

from utils import upload_template

from settings import MEMCACHED_MEMORY

@task        
def install_memcached():
    print(green("Task : %s, Executing on %s as %s" % ('setup_memcache', env.host, env.user)))
    
    Apt.install('memcached')
    
    upload_template('./server/etc/memcached.conf', '/etc/memcached.conf', 
                    use_sudo=True, use_jinja=True,
                    context={'MEMCACHED_MEMORY': MEMCACHED_MEMORY})
    
    

@task
@roles('webserver') 
def restart_memcached():
    sudo('service memcached restart')