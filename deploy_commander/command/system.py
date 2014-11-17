"""" 
System commands for deploy commander
"""
import os

from fabric.api import env
from fabric.contrib.files import is_link
from fabric.operations import run
from fabric.colors import yellow
from fabric.colors import green
from fabfile import utils


def symlink(params):
    """
    Create a symlink command.
    """
    source = params['source'] % env.params
    target = params['target'] % env.params
       
    if is_link(source):
        print source
        print(yellow("Symlink `%s` exists and will be removed" % source))
        run('rm %s' % source)
    
    
    command = "ln -s %s %s" % (target, source)
    run(command)
    
    print(green("Symlink from `%s` to `%s`." % (source, target))) 

def command(params):
    """
    Run a command
    """
    command = params['command'] % env.params
    run(command)

def upload_template(params):
    """
    Upload a template and render it with the given params.
    """
    
    cwd = os.getcwd()
    
    for key, value in params.iteritems():
        params[key] = value % env.params
    
    source = params['source']
    target = params['target']
    
    if 'use_sudo' in params:
        use_sudo = params['use_sudo']
    else:
        use_sudo = False
    
    current_path_template = "%s/.template/%s" % (cwd, source)  
    
    if not os.path.isfile(current_path_template):
        print(yellow("No template `%s` found in current path. It will fallback to deploy commander defaults" % (current_path_template)))
        template_dir = "%s/.template" % os.environ['DEPLOY_COMMANDER_ROOT_PATH']
    else:
        template_dir = "%s/.template" % cwd
        
    utils.upload_template(source, target,
                          use_sudo=use_sudo, use_jinja=True, 
                          context=params, template_dir=template_dir)
    
    print(green("Upload template from `%s/%s` to `%s`." % (template_dir, source, target))) 