"""" 
Main utils that can be used by the tasks.
"""

from fabric.contrib.files import upload_template as orig_upload_template
from fabric.operations import sudo
from fabric.operations import run
from fabric.api import env
from fabric.colors import yellow
from fabric.colors import red
from fabric.colors import green
from fabric.contrib.files import exists
from fabric.context_managers import hide
from fabric.operations import prompt
from fabric.utils import abort

from os import listdir
from os.path import isfile, join
        
        
def get_master_password():
    if not env.has_key('master_password') or len(env.master_password) == 0:
        abort(red("No master password configurated"))
    
    return env.master_password

def print_double_line():
    print("")
    print(green("================================================================================================="))
    print("")
    
def print_single_line():
    print("")
    print(green("-------------------------------------------------------------------------------------------------"))
    print("")

def format_params(params):
    """
    Take a dict of params and process them with the environment params
    """
    for key, value in params.iteritems():
        params[key] = value % env.params
    return params

def get_global_params(return_params, *params):
    """
    Tries to get global param values by name 
    """
    for param in params:
        if param in env.params:
            return_params[param] = env.params[param]
            
    return return_params

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

    if env.host in env.roledefs[group]["config"]:
        env.password = env.roledefs[group]["config"][env.host]["ssh_password"]
        env.user = env.roledefs[group]["config"][env.host]["ssh_user"]
        if 'ssh_keyfile' in env.roledefs[group]["config"][env.host]:
            env.key_filename = env.roledefs[group]["config"][env.host]["ssh_keyfile"]