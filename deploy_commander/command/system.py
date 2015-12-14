""""
System commands for deploy commander
"""
import os
import utils
import traceback
import config

from fabric.api import env
from fabric.contrib.files import is_link
from fabric.operations import run
from fabric.operations import sudo
from fabric.operations import get

from fabric.utils import abort

from fabric.colors import yellow
from fabric.colors import green

from fabric.context_managers import cd
from fabric.context_managers import settings
from fabric.context_managers import hide

def cleanup_old_files(params):
    abort(red("Command `cleanup_old_files` is depricated, use `filesystem_remove_old`"))

def filesystem_remove_old(params):
    """
    Delete old files and folders
    """
    params = utils.format_params(params)

    if not 'minutes' in params:
        params['minutes'] = 86400

    if not 'path' in params:
        abort('No path set')

    with settings(warn_only=True):
        run("find %s/* -maxdepth 0 -cmin +%s -exec rm -Rf {} \;" % (params['path'], params['minutes']))


# BUG : command doesn't work!?
# def filesystem_keep_latest(params):
#     """
#     Keep latest files and folders
#     """
#     params = utils.format_params(params)

#     if not 'releases' in params:
#         params['releases'] = 42

#     if not 'path' in params:
#         abort('No path set')

#     if not 'name' in params:
#         abort('No name set')

#     with settings(warn_only=True):
#         run("KEEPCOUNT=%s;find /projects/keeplatest -maxdepth 1 | grep %s | sort -rn | tail -n +$KEEPCOUNT+1 | while read folder; do rm -rf \"$folder\" ; done;" % (params['releases'], params['path'], params['name']))


def symlink(params):
    """
    Create a symlink command.
    """
    params = utils.format_params(params)

    if not 'source' in params:
        abort('No source set')

    if not 'target' in params:
        abort('No target set')

    if is_link(params['source']):
        print(yellow("Symlink `%s` exists and will be removed" % params['source']))
        run('rm %s' % params['source'])

    command = "ln -s %s %s" % (params['target'], params['source'])
    run(command)

    print(green("Symlink from `%s` to `%s`." % (params['source'], params['target'])))

def command(params):
    """
    Run a command
    """
    with hide('running'):
        params = utils.format_params(params)

        if not 'command' in params:
            abort('No command set')

        if 'use_sudo' in params:
            sudo(params['command'])
        else:
            run(params['command'])

    if 'secure' in params and params['secure'] == "True":
        print(green("Secure command executed"))
    else:
        print(green("Command `%s` executed" % params['command']))
        

def multi_command(params):
    """
    Run a command multiple times, based on config
    """
    with hide('running'):
        #params['command'] = utils.format_params(params, strict=False)
        if not 'command' in params:
            abort('No command set')

        #Skip command, we'll format it later on.. but we'll need it for the list_config_file..
        original_params = params.copy();
        del params['command']

        if not 'list_config_file' in params:
            abort('No list_config_file set')
      
        utils.format_params(params=params)
        
        data_list = config.read_config(params['list_config_file'])

        if data_list:
            for data in data_list:
                tmp_params = original_params.copy();
                tmp_params = utils.format_params(params=tmp_params, merge_extra_params=data)
                if 'use_sudo' in tmp_params:
                    sudo(tmp_params['command'])
                else:
                    run(tmp_params['command'])

                if 'secure' in params and params['secure'] == "True":
                    print(green("Secure command %s executed" % original_params['command']))
                else:
                    print(green("Command `%s` executed" % tmp_params['command']))
        else:
            if 'secure' in params and params['secure'] == "True":
                print(yellow("Command not executed, data list %s is empty" % (params['list_config_file'])))
            else:
                print(yellow("Command `%s` not executed, data list %s is empty" % (tmp_params['command'], params['list_config_file'])))
                

def ensure_path(params):
    """
    Ensure a certain path
    """
    params = utils.format_params(params)

    if not 'path' in params:
        abort('No path set')

    utils.ensure_path(path=params['path'])

    print(green("Ensure path `%s`." % (params['path'])))

def download_from_remote(params):
    """
    Download folder to local path
    """
    params = utils.format_params(params)

    if not 'remote_path' in params:
        abort('No remote path set')

    if not 'local_path' in params:
        abort('No local path set')

    print("Reading from `%s`" % params['remote_path'])
    print("Target to `%s`" % params['local_path'])

    try:
        get(**params)
    except Exception, e:
        print(str(e))

def upload_template(params):
    """
    Upload a template and render it with the given params.
    """

    cwd = os.getcwd()

    params = utils.format_params(params)

    if not 'use_sudo' in params:
        params['use_sudo'] = False

    if 'use_sudo' in params:
        use_sudo = params['use_sudo']
    else:
        use_sudo = False

    current_path_template = "%s/template/%s" % (cwd, params['source'])

    if not os.path.isfile(current_path_template):
        print(yellow("No template `%s` found in current path. It will fallback to deploy commander defaults" % (current_path_template)))
        template_dir = "%s/template" % os.environ['DEPLOY_COMMANDER_ROOT_PATH']
    else:
        template_dir = "%s/template" % cwd

    utils.upload_template(params['source'], params['target'],
                          use_sudo=use_sudo, use_jinja=True,
                          context=params, template_dir=template_dir)

    print(green("Upload template from `%s/%s` to `%s`." % (template_dir, params['source'], params['target'])))