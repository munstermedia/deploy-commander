from fabric.operations import sudo

from fabric.api import task

from settings import APT_INSTALL

class Apt(object):
    @staticmethod
    def install(*pkgs):
        sudo('apt-get install -y %s' % ' '.join(pkgs))

    @staticmethod
    def upgrade():
        sudo('apt-get update -y')
        sudo('apt-get upgrade -y')

@task
def setup_apt():
    Apt.install(*APT_INSTALL)