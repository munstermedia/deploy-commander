from fabric.api import task
from fabric.api import env

from fabric.utils import abort

import collections
import json
import pprint


env.source = {}
env.mysql_backup = {}
env.git = {}
env.stages = {}
env.site = {}

env.connection_attempts = 3
env.timeout = 30

@task
def tag(tag):
    # Set global tag
    env.tag = tag

@task
def project(project):
    if not project:
        abort("Enter project name")
    
    env.project_name = project
    env.project_folder = project
    env.domain = project 

@task
def environment(environment):
    if environment == 'dev':
        environment = 'development'
     
    if environment == 'prod':
        environment = 'production'   
    
    load_config('./config/default.json')
    
    load_config('./config/%s.json' % environment)
    
    env.env = environment
    
    if environment == 'dev' or environment == 'development':
        env.is_debug = 'True'
    
    if environment == 'prod' or environment == 'production':
        env.is_debug = 'False'
    
    # Set default project settings
    load_config('./config/%s/default.json' % (env.project_name))
    
    # Set specific env settings
    load_config('./config/%s/%s.json' % (env.project_name, environment))
        
    # When dev, create dev tag 
    if environment == 'development':
        tag('dev')

    pprint.pprint(env)

def load_config(filename):
    print "Set config %s" % (filename)
    with open(filename) as json_file:
        set_config(json.load(json_file))
     

def update(orig_dict, new_dict):
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
    if config.has_key('roledefs'):
        for setting_name, setting_value in config['roledefs'].iteritems():
            env.roledefs[setting_name] = setting_value
    
    
    if config.has_key('site'):
        env.site = update(env.site, config['site'])
    
    if config.has_key('source'):
        env.source = update(env.source, config['source'])
      
    if config.has_key('git'):
        env.git = update(env.git, config['git'])
            
    if config.has_key('mysql_backup'):
        env.mysql_backup = update(env.mysql_backup, config['mysql_backup'])

            
    if config.has_key('stages'):
        env.stages = update(env.stages, config['stages'])
