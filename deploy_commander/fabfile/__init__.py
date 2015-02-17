import sys
import os.path

sys.path.append(os.path.abspath(os.path.join(os.path.realpath(__file__), "../../")))

import json
import pprint
import utils
import config


from importlib import import_module

from fabric.api import task
from fabric.api import roles
from fabric.api import env
from fabric.api import runs_once
from fabric.api import hosts

from fabric.utils import abort

from fabric.contrib.files import exists

from fabric.operations import sudo
from fabric.operations import local

from fabric.colors import red
from fabric.colors import yellow
from fabric.colors import green

from fabric.contrib.console import confirm
from fabric.operations import prompt
from fabric.context_managers import hide



config.init()
   
@task
def runserver(environment='environment'):
    """ 
    Quick task to start running the webserver.
    """
    dc_application_path = os.path.dirname(os.path.realpath(__file__)) + '/../'
    dc_virtualenv_path = os.path.join(env.home_path, environment)
    
    local('environment/bin/gunicorn api:app'
          ' -e DC_HOME_PATH=%(dc_home_path)s'
          ' -e DC_VIRTUALENV_PATH=%(dc_virtualenv_path)s'
          ' -w 1' 
          ' -b 0.0.0.0:8686'
          ' --chdir %(dc_application_path)s' % {'dc_home_path':env.home_path,
                                                'dc_virtualenv_path':dc_virtualenv_path,
                                                'dc_application_path': dc_application_path});

@task
def home_path(home_path):
    """ 
    init with home path.
    used in system tasks where no current path is applicable
    """
    env.home_path = home_path

def set_project(project=None):
    """
    Checks if project is set, and if not it will prompt you to enter
    a valid project
    """
    if not 'project' in env.params:
        
        config_folder = "%s/config" % (env.home_path)
        available_projects = []
        for tmp_project in os.listdir(config_folder):
            if os.path.isdir(os.path.join(config_folder, tmp_project)):
                available_projects.append(tmp_project)
        
        if len(available_projects) == 0:
            abort(red("No projects available."))
            
        if not project:
            print(green("Available projects :"))
            print("")
            for project in available_projects:
                print("- %s" % project)
             
            print("")
            project = prompt('Enter project name : ', default=available_projects[0])
        
        if project not in available_projects:
            print(red("`%s` is not a valid project !" % project))
            set_project()
        else:
            env.params['project'] = project
    
def set_environment(environment=None):
    """
    Checks if environment is set, and if not it will prompt you to enter
    a valid project
    """
    if not 'environment' in env.params:
        if len(env.environments) == 0:
            abort(red("No environmens available."))
        
        if not environment:
            print(green("Available environments :"))
            print("")
            for environment in env.environments:
                print("- %s" % environment)
            
            print("")
            environment = prompt('Enter environment : ', default=env.environments[0])
        
        if environment not in env.environments:
            print("")
            print(red("`%s` is not a valid environment !" % environment))
            set_environment()
        else:
            # Set environment settings
            env.params['environment'] = environment
    
            config.environment()

def title_screen():
    """
    Prints out the title screen,... YEAH..
    """
    print(green("================================================================================================="))
    print(green("    ____             __               ______                                          __         "))
    print(green("   / __ \___  ____  / /___  __  __   / ____/___  ____ ___  ____ ___  ____ _____  ____/ /__  _____"))
    print(green("  / / / / _ \/ __ \/ / __ \/ / / /  / /   / __ \/ __ `__ \/ __ `__ \/ __ `/ __ \/ __  / _ \/ ___/"))
    print(green(" / /_/ /  __/ /_/ / / /_/ / /_/ /  / /___/ /_/ / / / / / / / / / / / /_/ / / / / /_/ /  __/ /    "))
    print(green("/_____/\___/ .___/_/\____/\__, /   \____/\____/_/ /_/ /_/_/ /_/ /_/\__,_/_/ /_/\__,_/\___/_/     "))
    print(green("          /_/            /____/                                                                  "))
    print(green("================================================================================================="))

@task
def encrypt_config():
    """
    Encrypt all json files to json.encrypt
    """
    title_screen()
    password = utils.get_master_password()
    
    for root, dirs, files in os.walk("./config"):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                
                config.write_encrypted_config(file_path,
                                              config.read_config(file_path))
                print(green("File `%s` encrypted." % file_path))
                os.remove(file_path)

@task   
def decrypt_config():
    """
    Decrypt all json.encrypt files to .json files
    """
    title_screen()
    password = utils.get_master_password()
    
    print(green("Decrypting..."))
    
    for root, dirs, files in os.walk("./config"):
        for file in files:
            if file.endswith(".encrypt"):
                encrypt_file_path = os.path.join(root, file)
                with open(encrypt_file_path) as ciphertext:
                    file_path = encrypt_file_path[:-8]
                    
                    config.write_config(file_path,
                                        config.read_config(file_path))
                    print(green("File `%s` decrypted." % encrypt_file_path))
                    os.remove(encrypt_file_path)


@task
def go(project=None, environment=None):
    """
    Default init for project actions
    """
    title_screen()
    
    utils.print_single_line()
    
    set_project(project)
    
    utils.print_single_line()
    
    set_environment(environment)
    
    utils.print_double_line()


@task 
def show_tasks():
    """
    List available tasks
    """
    if 'tasks' in env:
        print("Available tasks :")
        for key, val in env['tasks'].iteritems():
            if 'description' in val:
                print("%s : %s" % (green(key), val['description']))
            else:
                print("%s : ?" % green(key))
    else:
        print(red("No tasks defined?"))

@task
def show_task(task):
    """
    Show task info
    """
    if task in env['tasks']:
        print("Params :")
        print json.dumps(env.params, sort_keys=True, indent=4)
        print("Post params :")
        print json.dumps(env.post_params, sort_keys=True, indent=4)
        print("Task :")
        print json.dumps(env.tasks[task], sort_keys=True, indent=4)
    else:
        print(red("Invalid task `%s`" % task))

@task
def show_config():
    """
    Show current config settings from project and environment
    """
    utils.print_double_line()
    print json.dumps(env.params, sort_keys=True, indent=4)
    utils.print_double_line()
    print json.dumps(env.post_params, sort_keys=True, indent=4)
    utils.print_double_line()
    
    if 'commands' in env and len(env.commands) > 0:
        print(red("Commands are deprecated, use the name `tasks` instead"))
        env.tasks = env.commands
        
    if 'tasks' in env:
        for key, val in env['tasks'].iteritems():
            utils.print_double_line()
            print "Task `%s`" % key
            utils.print_double_line()
            if 'actions' in env['tasks'][key]:
                # Validate the basic settings
                for k, v in val['actions'].items():
                    if 'sequence' not in v:
                        v['sequence'] = "0"
                 
                actions = sorted(env['tasks'][key]['actions'].items(), key=lambda (k,v): v['sequence'])
                
                for key_action, current_action in actions:
                    print json.dumps(current_action, sort_keys=True, indent=4)
                    utils.print_single_line()
                    #pprint.pprint(current_action)

@task
@roles('webserver')   
def run(task):
    """
    Run task to execute the actions.
    Here's where it's all starting...
    """
    utils.init_env_settings('webserver')
    
    utils.print_double_line()
    
    if task not in env.tasks:
        abort(red("Task `%s` does not exist!" % task))
        
    if 'description' in env.tasks[task]:
        print(green(env.tasks[task]['description']))
    
    if 'input_params' in env.tasks[task]:
        for param_key, param_value in env.tasks[task]['input_params'].items():
            env.params[param_value['param']] = prompt(param_value['prompt'] + ' : ')
    
    ordered_tasks = sorted(env.tasks[task]['actions'].items(), key=lambda (k,v): v['sequence'])
    
    utils.print_single_line()
    
    for key_task, current_task in ordered_tasks:
        
        if 'description' in current_task:
            print(current_task['description'])
        else:
            print("Starting `%s`" % key_task)
        
        if 'execute' in current_task:
            print(red("The `execute` key is deprecated, use `command` instead!"))
        
        if not 'command' in current_task:
            abort(red("No valid command value in config"))
        
        print("Command : %s" % current_task['command'])
        print("")
        
        if 'enabled' in current_task and (current_task['enabled'] == False or current_task['enabled'] == "False"):
            print("Skipped : %s" % current_task['command'])
            continue
        
        
        
        if 'confirm' in current_task:
            if not confirm(current_task['confirm']):
                continue
            
        script = 'command.%s' % current_task['command']
        p, m = script.rsplit('.', 1)
        
        mod = import_module(p)
        task = getattr(mod, m)
         
        if 'params' in current_task:
            params = current_task['params']
        else:
            params = {}
        
        task(params = params)
        
        utils.print_single_line()
