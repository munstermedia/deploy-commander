"""" 
apt-get commands for deploy commander
"""

from fabric.operations import sudo
from fabric.colors import green
from fabric.utils import abort

def install(params):  
    """
    Install packages with apt-get.
    It will try to install without any confirmation prompt
    """
    abort(red("aptget is depricated, use puppet or chef for these kind of things."))
