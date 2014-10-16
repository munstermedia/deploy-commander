import os

from fabric.contrib.files import upload_template as orig_upload_template

from fabric.operations import sudo
from fabric.operations import run

from fabric.api import task
from fabric.api import env
from fabric.api import roles

from fabric.colors import green

from fabric.contrib.files import exists

def upload_template(src, dest, *args, **kwargs):
    """
    Wrapper around Fabric's upload_template that sets +r.

    upload_template does not preserve file permissions, http://code.fabfile.org/issues/show/117
    """
    orig_upload_template(src, dest, *args, **kwargs)
    sudo('chmod +r %s' % dest)
    
def ensure_path(path):
    parts = path.split('/')
    for i in range(2, len(parts)):
        tmp_parts = parts[0:(i+1)]
        tmp_path = '/'.join(tmp_parts)
        if not exists(tmp_path):
            print(green("Path %s created" % tmp_path))
            run('mkdir %s' % tmp_path)

@task
@roles('webserver') 
def run_python(): 
    sudo(os.path.join(env.virtualenv_project_tag, 'bin', 'python'))