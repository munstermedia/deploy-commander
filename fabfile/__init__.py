
import app


from fabric.api import task
from fabric.api import roles
from fabric.api import env
from fabric.api import runs_once
from fabric.api import hosts

from fabric.contrib.files import exists

from fabric.operations import sudo
from fabric.operations import local

from settings import tag
from settings import environment
from settings import project




         
