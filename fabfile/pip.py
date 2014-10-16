import os.path

from fabric.api import task

from fabric.operations import run
from fabric.operations import sudo
from fabric.operations import put

from fabric.contrib.files import exists

from fabric.api import env

from fabric.context_managers import shell_env

from utils import ensure_path

     
@task
def setup_pip_project():
    # Ensure download cache for pip
    with shell_env(PIP_DOWNLOAD_CACHE="%s/.pip_download_cache" % env.user_path):
        # Make sure virtualenv is installed
        sudo('pip install virtualenv')
        
        # Ensure the path exists
        ensure_path(env.virtualenv_project_path)
        
        # Create virtualenv if not existing
        if not exists(env.virtualenv_project_tag):
            run('virtualenv %s' % env.virtualenv_project_tag)
        
        # Remote filename on the server
        remote_filename = './tmp_requirements.txt'
        
        # Create pip command
        pip =  os.path.join(env.virtualenv_project_tag, 'bin', 'pip')
        
        # Copy requirements to server
        put('%s/requirements.txt' % (env.local_project_path), remote_filename)
        
        # Install requirements on server
        run('%s install -r %s' % (pip, remote_filename))
        
        # Remove temp requirements file
        run('rm %s' % remote_filename)
