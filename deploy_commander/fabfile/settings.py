import collections
import json

import os

from fabric.api import task
from fabric.api import env
from fabric.utils import abort

from fabric.colors import red
from fabric.colors import yellow
from fabric.colors import green

env.warn_only = False

env.params = {}
env.post_params = {}
env.actions = {}

env.connection_attempts = 3
env.timeout = 30


def init():
    """
    Default init
    """
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

def load_config(filename):
    """
    Load config by filename and set it...
    """
    
    cwd = os.getcwd()
    
    current_path_config_file = "%s/%s" % (cwd, filename)  
    
    if not os.path.isfile(current_path_config_file):
        print(yellow("No config `%s` found." % current_path_config_file))
    else:
        # Load config and process with set_config
        print(green("Load config %s" % (current_path_config_file)))
        with open(current_path_config_file) as json_file:
            set_config(json.load(json_file))

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
    if config.has_key('environments'):
        env.environments = config['environments']
    
    if config.has_key('roledefs'):
        for setting_name, setting_value in config['roledefs'].iteritems():
            env.roledefs[setting_name] = setting_value
    
    if config.has_key('params'):
        env.params = update(env.params, config['params'])
       
    if config.has_key('post_params'):
        env.post_params = update(env.post_params, config['post_params'])
         
    if config.has_key('actions'):
        env.actions = update(env.actions, config['actions'])
