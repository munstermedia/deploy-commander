"""" 
System commands for deploy commander
"""

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
    source = params['source'] % env.params
    target = params['target'] % env.params
    
    if 'use_sudo' in params:
        use_sudo = params['use_sudo']
    else:
        use_sudo = False
    
    utils.upload_template('./.templates/%s' % source, target,
                          use_sudo=use_sudo, use_jinja=True, context=params),