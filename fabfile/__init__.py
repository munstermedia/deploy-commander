
import app
from importlib import import_module

from fabric.api import task
from fabric.api import roles
from fabric.api import env
from fabric.api import runs_once
from fabric.api import hosts

from fabric.contrib.files import exists

from fabric.operations import sudo
from fabric.operations import local

from settings import environment
from settings import project

from fabric.colors import red
from fabric.colors import yellow
from fabric.colors import green

from fabfile import utils
import pprint

from fabric.contrib.console import confirm
from fabric.operations import prompt

import settings

@task
def go():
    if not 'project' in env.params or env.params['project']:
        project_name = prompt('Enter project name : ', default="example")
        
        settings.project(project_name)
    
    if not 'environment' in env.params or env.params['environment']:
        environment_name = prompt('Enter environment : ', default="development")
            
        settings.environment(environment_name)

@task
@roles('webserver')   
def run(action):
    
    utils.init_env_settings('webserver')
    
    print(green(env.actions[action]['title']))
    
    
    if 'input_params' in env.actions[action]:
        for param_key, param_value in env.actions[action]['input_params'].items():
            env.params[param_value['param']] = prompt(param_value['prompt'])
    
    ordered_actions = sorted(env.actions[action]['commands'].items(), key=lambda (k,v): v['sequence'])
    
    for key_action, current_action in ordered_actions:
        print("Run `%s`" % key_action)
       
        if 'confirm' in current_action:
            if not confirm(current_action['confirm']):
                continue
            
        script = 'fabfile.command.%s' % current_action['command']
        p, m = script.rsplit('.', 1)

        mod = import_module(p)
        command = getattr(mod, m)
         
        command(params = current_action['params'])
        
    