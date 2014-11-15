"""" 
Main utils that can be used by the commands.
"""

from fabric.contrib.files import upload_template as orig_upload_template
from fabric.operations import sudo
from fabric.operations import run
from fabric.api import env
from fabric.colors import yellow
from fabric.contrib.files import exists


def upload_template(src, dest, *args, **kwargs):
    """
    Wrapper around Fabric's upload_template that sets +r.

    upload_template does not preserve file permissions, http://code.fabfile.org/issues/show/117
    """
    orig_upload_template(src, dest, *args, **kwargs)
    
def ensure_path(path, use_sudo=False):
    """
    This will check if the path exists, if not it wil try to create
    it recursively by 2 folders depth from the path
    """
    
    parts = path.split('/')
    for i in range(2, len(parts)):
        tmp_parts = parts[0:(i+1)]
        tmp_path = '/'.join(tmp_parts)
        if not exists(tmp_path):
            if use_sudo:
                sudo('mkdir %s' % tmp_path)
            else:
                run('mkdir %s' % tmp_path)
                
            print(yellow("Path `%s` did not exist and is created" % tmp_path))

    
def init_env_settings(group):
    """
    Set setting by enviroment and group.
    This will be used for generic settings that must be used by the system.
    """
    env.password = env.roledefs[group]["config"][env.host]["ssh_password"]
    env.user = env.roledefs[group]["config"][env.host]["ssh_user"]