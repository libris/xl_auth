# -*- coding: utf-8 -*-
"""Root Python package providing KB ``xl_auth`` OAuth2 provider."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json
from os import path

__all__ = ['__name__', '__version__']


def _read_package_json_version():
    with open(path.join(path.dirname(__file__), '..', 'package.json')) as package_json:
        return json.load(package_json)['version']


__name__ = 'xl_auth'

__version__ = _read_package_json_version()
