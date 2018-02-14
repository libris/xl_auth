# -*- coding: utf-8 -*-
"""Create an application instance."""

from __future__ import absolute_import, division, print_function, unicode_literals

import re
import sys

from flask.cli import main as flask_cli_main
from flask.helpers import get_debug_flag

from xl_auth.app import create_app
from xl_auth.settings import DevConfig, ProdConfig


def main():
    flask_cli_main()


#CONFIG = DevConfig if get_debug_flag() else ProdConfig
#app = create_app(CONFIG)
