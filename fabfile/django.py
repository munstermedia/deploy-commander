import os.path

from fabric.api import task
from fabric.api import env
from fabric.api import roles

from fabric.operations import run
from fabric.operations import sudo

from fabric.utils import abort


@task
@roles('webserver')
def django_manage(action):
    if not env.has_key('project_name'):
        abort("Run `project:<project name>` first")
    
    if not env.has_key('tag'):
        abort("Run `tag:<tag>` first")
    
    virtual_env_path = os.path.join(env.virtualenv_project_tag, 'bin', 'python')
    sudo('%s %s/manage.py %s' % (virtual_env_path, env.source_project_tag , action))

