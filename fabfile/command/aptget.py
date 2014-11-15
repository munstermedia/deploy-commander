"""" 
apt-get commands for deploy commander
"""

from fabric.operations import sudo
from fabric.colors import green


def install(params):  
    """
    Install packages with apt-get.
    It will try to install without any confirmation prompt
    """
    sudo('apt-get update')
    
    sudo('apt-get install -y %s' % (params['package']))
    print(green("`%s` successfully installed" % params['package']))
