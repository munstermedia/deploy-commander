"""" 
System commands for deploy commander
"""
import os

from fabric.api import env
from fabric.contrib.files import is_link
from fabric.operations import run
from fabric.operations import get

from fabric.utils import abort

from fabric.colors import yellow
from fabric.colors import green
from fabfile import utils

def symlink(params):
    """
    Create a symlink command.
    """
    params = utils.format_params(params)
       
    if is_link(params['source']):
        print(yellow("Symlink `%s` exists and will be removed" % params['source']))
        run('rm %s' % params['source'])
    
    command = "ln -s %s %s" % (params['target'], params['source'])
    run(command)
    
    print(green("Symlink from `%s` to `%s`." % (params['source'], params['target']))) 
    
def command(params):
    """
    Run a command
    """
    command = params['command'] % env.params
    run(command)
    
    print(green("Command `%s` executed" % command)) 


def download_from_remote(params):
    """
    Download folder to local path
    """
    params = utils.format_params(params)
    
    if not 'remote_path' in params:
        abort('No remote path set')
        
    if not 'local_path' in params:
        abort('No local path set')
    
    get(**params) 

def upload_template(params):
    """
    Upload a template and render it with the given params.
    """
    
    cwd = os.getcwd()
    
    params = utils.format_params(params)
    
    if 'use_sudo' in params:
        use_sudo = params['use_sudo']
    else:
        use_sudo = False
    
    current_path_template = "%s/template/%s" % (cwd, params['source'])  
    
    if not os.path.isfile(current_path_template):
        print(yellow("No template `%s` found in current path. It will fallback to deploy commander defaults" % (current_path_template)))
        template_dir = "%s/template" % os.environ['DEPLOY_COMMANDER_ROOT_PATH']
    else:
        template_dir = "%s/template" % cwd
        
    utils.upload_template(params['source'], params['target'],
                          use_sudo=use_sudo, use_jinja=True, 
                          context=params, template_dir=template_dir)
    
    print(green("Upload template from `%s/%s` to `%s`." % (template_dir, params['source'], params['target']))) 