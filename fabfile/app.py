import os.path
import os
import utils
import pprint
import mysql

from fabric.api import task
from fabric.api import env
from fabric.api import roles

from fabric.contrib.files import exists

from fabric.operations import sudo
from fabric.operations import run
from fabric.operations import prompt

from fabric.utils import abort

from fabric.colors import red
from fabric.colors import yellow

from fabric.utils import abort


from fabric.contrib.console import confirm

from fabric.context_managers import cd

@task
@roles('webserver')
def install():
    if not env.has_key('project_folder'):
        abort('No project known, execute with `fab project:name` first')
    
    utils.init_env_settings('webserver')
     
    url_params = {'project_folder':env.project_folder,
                  'user':env.user,
                  'tag':env.tag,
                  'domain':env.site['domain']}
    
    repo_path = env.source['repo_path'] % url_params
    utils.ensure_path(repo_path)
    
    with cd(repo_path):
        run('git clone --recursive %s %s' % (env.git['repo_url'], repo_path))
         
      
@task
@roles('webserver')
def rollback_app():  
    if env.env == 'development':
        abort(red("Rollback on development? :)"))

    if not env.tag:
        abort("Run `tag:<tagname>` first")


@task
@roles('webserver')
def deploy():
    if not env.tag:
        abort("Run with `tag:<tagname>`")
    
    if len(env.tag) == 0:
        abort(red("Invalid tag"))
    
    utils.init_env_settings('webserver')
    
    url_params = {'project_folder':env.project_folder,
                  'user':env.user,
                  'tag':env.tag,
                  'domain':env.site['domain']}
    
    repo_path = env.source['repo_path'] % url_params
    current_path = env.source['current_path'] % url_params
    tag_path = env.source['tag_path'] % url_params
    
    if not exists(repo_path):
        abort("Repo path not existing... is the project installed? ")
    
    # If exist remove full source
    if exists(tag_path):
        run('rm -Rf %s' % tag_path)
    
    utils.ensure_path(tag_path)
    
    with cd(repo_path):
        run('git fetch')
        # Update local repo with latest code
        run('git checkout %s' % (env.tag))
     
        run('git pull origin %s --recurse-submodules' % (env.tag))
         
        run('git submodule update')
    
    # Copy source code to version
    run('cp -R %s/* %s' % (repo_path, tag_path))
    
    process_stage('after_checkout')
            
    if env.has_key('mysql_backup'):
        mysql.backup()
        process_stage('after_mysql_backup')
    
        
    # Final live,... create symlink to current folder
    if exists(current_path):
        run('rm %s' % current_path)
    
    run('ln -s %s %s' % (tag_path, current_path))
    
@task
@roles('webserver')   
def process_stage(stage):
    utils.init_env_settings('webserver')
    
    url_params = {'project_folder':env.project_folder,
                  'user':env.user,
                  'tag':env.tag,
                  'domain':env.site['domain']}
        
    if stage in env.stages and len(env.stages[stage]) > 0:
        for task_key, task in env.stages[stage].iteritems():
            if task['action'] == 'execute-command':
                command = task['command'] % url_params
                run(command)
                
            if task['action'] == 'push-template':
                print task['action']
                source = task['source'] % url_params
                target = task['target'] % url_params
                
                if 'use_sudo' in task:
                    use_sudo = task['use_sudo']
                else:
                    use_sudo = False
                
                utils.upload_template('./templates/%s' % source, target,
                                      use_sudo=use_sudo, use_jinja=True, context=task['params']),
                                      
    