import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pprint

import fabfile.utils
import fabfile.config

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

def set_project():
    """
    Checks if project is set, and if not it will prompt you to enter
    a valid project
    """
    if not 'project' in env.params or env.params['project']:
        cwd = os.getcwd()
        config_folder = "%s/config" % (cwd)
        
        print(green("Available projects :"))
        print("")
        available_projects = []
        for project in os.listdir(config_folder):
            if os.path.isdir(os.path.join(config_folder, project)):
                available_projects.append(project)
                print("- %s" % project)
            
        if len(available_projects) == 0:
            abort("No projects available.")
            
        print("")
        project_name = prompt('Enter project name : ', default=available_projects[0])
        if project_name not in available_projects:
            print(red("`%s` is not a valid project !" % project_name))
            set_project()
        
        env.params['project'] = project_name
    
def set_environment():
    """
    Checks if environment is set, and if not it will prompt you to enter
    a valid project
    """
    if not 'environment' in env.params or env.params['environment']:
        if len(env.environments) == 0:
            abort("No environmens available.")
        
        print(green("Available environments :"))
        print("")
        for environment in env.environments:
            print("- %s" % environment)
        
        print("")
        environment_name = prompt('Enter environment : ', default=env.environments[0])
        
        if environment_name not in env.environments:
            print("")
            print(red("`%s` is not a valid environment !" % environment_name))
            set_environment()
        
        # Set environment settings
        env.params['environment'] = environment_name
    
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
def go():
    """
    Default init for project actions
    """
    title_screen()
    
    utils.print_single_line()
    
    set_project()
    
    utils.print_single_line()
    
    set_environment()
    
    utils.print_double_line()

@task
@roles('webserver')   
def run(command):
    """
    Run command to execute the actions.
    Here's where it's all starting...
    """
    utils.init_env_settings('webserver')
    
    utils.print_double_line()
    
    if 'description' in env.commands[command]:
        print(green(env.commands[command]['description']))
    
    if 'input_params' in env.commands[command]:
        for param_key, param_value in env.commands[command]['input_params'].items():
            env.params[param_value['param']] = prompt(param_value['prompt'])
    
    ordered_commands = sorted(env.commands[command]['actions'].items(), key=lambda (k,v): v['sequence'])
    
    utils.print_single_line()
    
    for key_command, current_command in ordered_commands:
        
        if 'description' in current_command:
            print(current_command['description'])
        else:
            print("Starting `%s`" % key_command)
        
        if not 'execute' in current_command:
            abort(red("No valid execute value in config"))
        
        print("Execute : %s" % current_command['execute'])
        print("")
        
        
        
        if 'confirm' in current_command:
            if not confirm(current_command['confirm']):
                continue
            
        script = 'command.%s' % current_command['execute']
        p, m = script.rsplit('.', 1)
        
        mod = import_module(p)
        command = getattr(mod, m)
         
        if 'params' in current_command:
            params = current_command['params']
        else:
            params = {}
        
        command(params = params)
        
        utils.print_single_line()
