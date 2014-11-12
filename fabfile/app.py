import os.path
import os
import utils
import pprint

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
     
    params = {'project_folder':env.project_folder,
              'user':env.user,
              'tag':env.tag}
    
    repo_path = env.source['repo_path'] % params
    utils.ensure_path(repo_path)
    
    with cd(repo_path):
        run('git clone --recursive %s %s' % (env.git['repo_url'], repo_path))
    #run('git clone --recursive %s %s' % (env.git['repo_url'], repo_path))
         
      
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
    
    params = {'project_folder':env.project_folder,
              'user':env.user,
              'tag':env.tag}
    
    repo_path = env.source['repo_path'] % params
    utils.ensure_path(repo_path)
    
    tag_path = env.source['tag_path'] % params

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
    run('cp -R %s %s' % (repo_path, tag_path))
    