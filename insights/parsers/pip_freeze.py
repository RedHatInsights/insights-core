"""
pip freeze - Command
====================

This module provides the python packages installed in a virtualenv, gathered
from the ``pip freeze`` command.

The parser breaks out each python package into <pkg_name> and <version>, stored
in two parallel arrays.

Typical output of pip freeze is::
    requests==2.21.0
    scandir==1.10.0
    simplegeneric==0.8.1
    six==1.12.0
    traitlets==4.3.2
    typing==3.6.6
    urllib3==1.24.1
    wcwidth==0.1.7

Attributes:

    venv_dir (string): virtualenv directory where the packages live
    pkg_names (list): the package name only i.e. requests
    pkg_version (list): version portion of the package i.e. 1.3.1
    pkgs (list): full package name i.e. requests==1.3.1

Examples:
    

"""
import os
from insights.specs import Specs
from insights import Parser, parser

BASE_DIR = '/var/lib/awx'


@parser(Specs.tower_pip_freeze)
class PipFreeze(Parser):
    def parse_content(self, content):

        # For testing. I couldn't get at this class to mock the args
        venv_dir = 'foobar'
        if hasattr(self, 'args') and self.args:
            venv_dir = self.args

        self.venv_dir = os.path.join(BASE_DIR, venv_dir)

        self.pkg_names = []
        self.pkg_versions = []
        self.pkgs = []

        for line in content:
            try:
                pkg, version = line.split('==')
            except ValueError:
                continue

            self.pkgs.append(line)
            self.pkg_names.append(pkg)
            self.pkg_versions.append(version)
