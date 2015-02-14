"""" 
git commands for deploy commander
"""

from fabric.api import env
from fabric.contrib.files import exists
from fabric.operations import run
from fabric.operations import prompt
from fabric.utils import abort
from fabric.colors import red
from fabric.colors import yellow
from fabric.colors import green
from fabric.contrib.console import confirm
from fabric.context_managers import cd
from fabric.context_managers import hide
from fabric.context_managers import show

import utils


def install_repo(params):
    abort(red("install_repo is deprecated, use git.clone instead."))

def clone(params):
    """
    The clone command can be used to clone a new repo.
    If it's allready an existing path it will prompt for overwrite
    """
    
    if 'repo_path' in params:
        abort(red("repo_path is deprecated, use git_repo_path"))
        
    if 'repo_url' in params:
        abort(red("repo_url is deprecated, use git_repo_url"))
      
    # Try to get global params
    params = utils.get_global_params(params,
                                     'git_repo_path', 
                                     'git_repo_url')
    
    if 'git_repo_path' not in params:
        abort(red("git_repo_path can't be empty?"))
    
    if 'git_repo_url' not in params:
        abort(red("git_repo_url can't be empty?"))
    
    params = utils.format_params(params)
    
    if exists(params['git_repo_path']):
        if confirm("Repo path `%s` found, do you want to reinstall?" % params['git_repo_path']):
            print(yellow("Repo path `%s` will be deleted" % params['git_repo_path']))
            run('rm -Rf %s' % params['git_repo_path'])
        else:
            abort("Aborted...")
        
    utils.ensure_path(params['git_repo_path'])
    
    run('git clone --recursive %s %s' % (params['git_repo_url'], params['git_repo_path']))
         
    print(green("Repo `%s` successfully cloned" % params['git_repo_url']))

def deploy_tag(params):
    """
    Deprecated command, use deploy instead
    """
    abort(red("Warning git.deploy_tag is deprecated, Use git.deploy instead!"))

def deploy(params):
    """
    This command will update a repo and copy the contents to another folder.
    It can be used to create versioned deployments of the codebase
    When executed it will prompt for the tag to deploy if it's not known
    """
    
    # Try to get global params
    params = utils.get_global_params(params,
                                     'git_repo_path', 
                                     'git_repo_url',
                                     'git_branch',
                                     'git_source_path')
    
    # Old params
    if 'tag_path' in params:
        abort(red("Warning tag_path is deprecated, Use git_source_path !"))
    
    if 'target_path' in params:
        abort(red("Warning target_path is deprecated, Use git_source_path !"))
    
    if 'tag' in params:
        abort(red("Warning tag is deprecated, Use git_branch !"))
        
    if 'branch' in params:
        abort(red("Warning branch is deprecated, Use git_branch !"))
       
    if 'repo_path' in params:
        abort(red("repo_path is deprecated, use git_repo_path !")) 
        
    
    # Check required params
    if 'git_source_path' not in params:
        abort(red("git_source_path is required !")) 
    
    if 'git_repo_url' not in params:
        abort(red("git_repo_url is required !")) 
    
    if 'git_repo_path' not in params:
        abort(red("git_repo_path is required !")) 
        
    if 'git_branch' not in params or len(params['git_branch']) == 0:
        abort(red("`git_branch` is required !"))
    
    params = utils.format_params(params)
    
    if not exists(params['git_repo_path']):
        abort(red("Repo path not existing... is the project installed?"))
    
    # If exist remove full source
    if exists(params['git_source_path']):
        print(yellow("Deploy target path `%s` allready existed... source data be removed and reset." % params['git_source_path']))
        run('rm -Rf %s' % params['git_source_path'])
    
    utils.ensure_path(params['git_source_path'])
    
    with cd(params['git_repo_path']):
        run('git fetch')
        
        # Update local repo with latest code
        run('git checkout %s' % (params['git_branch']))
        
        run('git pull origin %s' % (params['git_branch']))
        
        run('git submodule update')
        
        # Copy source code to version
        run('cp -Rf %s/* %s/' % (params['git_repo_path'], params['git_source_path']))
    
            