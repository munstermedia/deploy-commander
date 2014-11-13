from fabric.api import task
from fabric.api import env

from fabric.utils import abort

import json
import pprint


env.source = {}
env.mysql_backup = {}

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



def load_config(filename):
    print "Set config %s" % (filename)
    with open(filename) as json_file:
        set_config(json.load(json_file))
     
def set_config(config):
    if config.has_key('roledefs'):
        for setting_name, setting_value in config['roledefs'].iteritems():
            env.roledefs[setting_name] = setting_value
    
    if config.has_key('source'):
        for setting_name, setting_value in config['source'].iteritems():
            env.source[setting_name] = setting_value
            
    if config.has_key('mysql_backup'):
        for setting_name, setting_value in config['mysql_backup'].iteritems():
            env.mysql_backup[setting_name] = setting_value
