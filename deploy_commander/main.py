import sys
import os
from fabric.main import main as fab_main

def main():
    main_root = os.path.dirname(__file__)

    os.environ['DEPLOY_COMMANDER_ROOT_PATH'] = main_root

    fab_main(fabfile_locations=[os.path.join(main_root, 'fabfile')])

