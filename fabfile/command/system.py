import os.path
import os

import pprint
import mysql

from fabric.api import task
from fabric.api import env
from fabric.api import roles

from fabric.contrib.files import exists
from fabric.contrib.files import is_link

from fabric.operations import sudo
from fabric.operations import run
from fabric.operations import prompt

from fabric.utils import abort

from fabric.colors import red
from fabric.colors import yellow
from fabric.colors import green

from fabric.utils import abort

from fabfile import utils

from fabric.contrib.console import confirm

from fabric.context_managers import cd

def symlink(params):
    
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
    command = params['command'] % env.params
    run(command)
    
def upload_template(params):
    source = params['source'] % env.params
    target = params['target'] % env.params
    
    if 'use_sudo' in params:
        use_sudo = params['use_sudo']
    else:
        use_sudo = False
    
    utils.upload_template('./.templates/%s' % source, target,
                          use_sudo=use_sudo, use_jinja=True, context=params),