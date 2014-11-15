import os.path
import os
import fabfile.utils
import pprint
import mysql

from fabric.api import task
from fabric.api import env
from fabric.api import roles

from fabric.contrib.files import exists
from fabric.contrib.files import is_link

from fabric.operations import sudo
from fabric.operations import run
from fabric.operations import prompt

from fabric.utils import abort

from fabric.colors import red
from fabric.colors import yellow
from fabric.colors import green

from fabric.utils import abort

from fabric.operations import prompt
from fabric.contrib.console import confirm

from fabric.context_managers import cd

from fabfile import utils
from fabric.utils import abort

def install(params):
    
    sudo('apt-get install -y %s' % (params['package']))
         
    print(green("`%s` successfully installed" % params['package']))
