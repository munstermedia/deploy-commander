import collections
import json

import os
import utils

import time

from fabric.api import task
from fabric.api import env
from fabric.utils import abort

from fabric.colors import red
from fabric.colors import yellow
from fabric.colors import green


from simplecrypt import encrypt
from simplecrypt import decrypt
from simplecrypt import DecryptionException


# Set default connection_attempts
env.connection_attempts = 3

# Set default timeout
env.timeout = 30

# Root path of home where all the files will live..
env.home_path = os.getcwd()

# Base params settings
env.params = {}

# Base post params setting
env.post_params = {}

# Commands setting deprecated
env.commands = {}

# Tasks setting
env.tasks = {}

# Mail settings
env.mail = {}

# Sequence of loading
env.config_load_strategy = ['config/default.json',
                            'config/%(environment)s.json',
                            'config/%(project)s/default.json',
                            'config/%(project)s/%(environment)s.json'
                            ]

def init():
    """
    Default init for all commands
    """
    env.stdout = False
    env.running = False
    env.environments = ["development", "production", "staging", "testing"]
    
    # Load main config
    load_main_config()
     
    env.debug = False 
    env.warning_only = True
    env.stdout = False
    env.running = False
    env.params['timestamp'] = int(time.time())
    
    
    

def environment(): 
    """
    Load environment settings and process the post_params
    """
    project_config = 'config/%s/config.json' % (env.params['project'])
    if os.path.isfile(project_config):
        print(green("Load project config %s" % (project_config)))
        with open(project_config) as json_config:
            try:
                main_config = json.load(json_config)
            except Exception, e:
                abort(red("Cannot read main config, is the config correct?. `%s`" % e))
            
            if 'config_load_strategy' in main_config:
                env.config_load_strategy = main_config['config_load_strategy']
    
    if 'config_load_strategy' in env:
        for config_file in env['config_load_strategy']:
            load_config(config_file % env.params)
                    
    # Post process params from params
    if env.post_params:
        print ""
        for param_key, param_value in env.post_params.iteritems():
            env.params[param_key] = param_value % env.params
            print(yellow("Set post param `%s` to `%s`" % (param_key, env.params[param_key])))

def write_encrypted_config(file_path, config):
    """
    Takes a config dict and formats it to a json string
    It will be encrypted and then stored as json.encrypt file
    """
    if file_path.endswith(".json"):
        encrypt_file_path = "%s.encrypt" % file_path
        json_config = dicttoconfig(config)
        with open(file_path) as encrypted_file:
            password = utils.get_master_password()
            
            try:
                ciphertext = encrypt(password, json_config)
            except DecryptionException, e:
                abort(red(e))
            
            encrypted_file = open(encrypt_file_path, "w")
            encrypted_file.write(ciphertext)
            encrypted_file.close()

def read_config(file_path):
    """
    Tries to read config from 2 types of files.
    If json file is available it will use that one.
    If there is no json file it will use the encrypted file.
    """
    if file_path.endswith(".json"):
        if os.path.isfile(file_path):
            print(green("Load config %s" % (file_path)))
            with open(file_path) as json_config:
                try:
                    return json.load(json_config)
                except Exception, e:
                    abort(red("Cannot read config, is the config correct?. `%s`" % e))
                
        encrypt_file_path = "%s.encrypt" % file_path
        
        if not os.path.isfile(encrypt_file_path):
            abort(red("No config `%s` found." % encrypt_file_path))
        
        with open(encrypt_file_path) as ciphertext:
            password = utils.get_master_password()
            
            try:
                config = decrypt(env.master_password, ciphertext.read()).decode('UTF-8')
            except DecryptionException, e:
                abort(red(e))
            try:
                return json.loads(config)
            except Exception, e:
                abort(red("Cannot read config, is the config correct? `%s`" % e))
            
        return {}
    
def dicttoconfig(config):
    """
    Generic function to create json string from dict
    """
    try:
        json_content = json.dumps(config, sort_keys=True, indent=4)
    except Exception, e:
        abort(red(e))
        
    return json_content
   
def write_config(file_path, config):
    """
    Write binary config file
    """
    
    json_config = dicttoconfig(config)
    with open(file_path, "wb") as config_file:
        config_file.write(json_config)
        config_file.close()
    

def str2bool(v):
  """
  Helper to check true/false value of config setting
  """
  return v.lower() in ("yes", "true", "t", "1")

def load_main_config():
    """
    Load main config file.
    """
    
    old_file_path = "%s/.config" % (env.home_path)
    if os.path.isfile(old_file_path):
        abort(red("The main config file `%s` is deprecated in this version of deploy commander, please rename file to config.json" % (old_file_path)))
    
    file_path = "%s/config.json" % (env.home_path)
    if not os.path.isfile(file_path):
        abort(red("No main config file found. Did you setup your project in the `%s` file?" % (file_path)))
    else:
        with open(file_path) as json_config:
            config = json.load(json_config)
            if not 'master_password' in config:
                abort(red('No master password set in main config.'))
            
            env.master_password = config['master_password']
            
            # If environment is set in config
            if 'env' in config:
                if 'debug' in config['env']:
                    env.debug = str2bool(config['env']['debug'])
                    
                if 'warning_only' in config['env']:
                    env.warning_only = str2bool(config['env']['warning_only'])
            
                if 'running' in config['env']:
                    env.running = str2bool(config['env']['running'])
            
                if 'stdout' in config['env']:
                    env.stdout = str2bool(config['env']['stdout'])
            
            if 'mail' in config:
                env.mail = config['mail']
    
def load_config(filename):
    """
    Load config by filename and set it...
    """
    
    file_path = "%s/%s" % (env.home_path, filename)
    
    config = read_config(file_path)
    if config:
        set_config(config)

def update(orig_dict, new_dict):
    """
    Method to recusively overwrite dicts.
    This is used to merge the configs to one config
    """
    
    for key, val in new_dict.iteritems():
        if isinstance(val, collections.Mapping):
            tmp = update(orig_dict.get(key, { }), val)
            orig_dict[key] = tmp
        elif isinstance(val, list):
            orig_dict[key] = (orig_dict[key] + val)
        else:
            orig_dict[key] = new_dict[key]
    return orig_dict

def set_config(config):
    """
    Main set config.
    This will check certain key/values in the configuration file and 
    tries to merge them together
    """
    
    if config.has_key('roledefs'):
        for setting_name, setting_value in config['roledefs'].iteritems():
            env.roledefs[setting_name] = setting_value
    
    if config.has_key('params'):
        env.params = update(env.params, config['params'])
       
    if config.has_key('post_params'):
        env.post_params = update(env.post_params, config['post_params'])
         
    if config.has_key('tasks'):
        env.tasks = update(env.tasks, config['tasks'])

