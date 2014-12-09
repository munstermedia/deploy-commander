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

from fabric.state import output

from simplecrypt import encrypt
from simplecrypt import decrypt
from simplecrypt import DecryptionException

env.warn_only = False

env.params = {}
env.post_params = {}
env.commands = {}

env.connection_attempts = 3
env.timeout = 30

from fabric.state import output

def init():
    """
    Default init for all commands
    """

    # Default output settings
    output['running'] = False
    output['stdout'] = False

    env.environments = ["development", "production", "staging", "testing"]
    
    # Load main config
    load_main_config()
      
    env.params['timestamp'] = int(time.time())
    
    # Load default
    load_config('config/default.json')
    

def environment(): 
    """
    Load environment settings and process the post_params
    """
    
    # Load environment config
    load_config('config/%s.json' % env.params['environment'])
    
    # Load default project settings
    load_config('config/%s/default.json' % (env.params['project']))
    
    # Load specific env settings
    load_config('config/%s/%s.json' % (env.params['project'], env.params['environment']))
    
    # Post process params from params
    if env.post_params:
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
    
def load_main_config():
    """
    Load main config file.
    """
    cwd = os.getcwd()
    
    file_path = "%s/.config" % (cwd)
    if not os.path.isfile(file_path):
        abort(red("No main config file found. Did you setup your project in the `%s` file?" % (file_path)))
    else:
        with open(file_path) as json_config:
            config = json.load(json_config)
            if not 'master_password' in config:
                abort(red('No master password set in main config.'))
            
            env.master_password = config['master_password']
    
def load_config(filename):
    """
    Load config by filename and set it...
    """
    
    cwd = os.getcwd()
    
    file_path = "%s/%s" % (cwd, filename)
    
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
    if config.has_key('output'):
        for setting_name, setting_value in config['output'].iteritems():
            output[setting_name] = setting_value
    
    if config.has_key('roledefs'):
        for setting_name, setting_value in config['roledefs'].iteritems():
            env.roledefs[setting_name] = setting_value
    
    if config.has_key('params'):
        env.params = update(env.params, config['params'])
       
    if config.has_key('post_params'):
        env.post_params = update(env.post_params, config['post_params'])
         
    if config.has_key('commands'):
        env.commands = update(env.commands, config['commands'])

