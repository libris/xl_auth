# -*- coding: utf-8 -*-
"""Test :py:mod:`xl_auth` package identifiers."""

from __future__ import print_function, absolute_import, unicode_literals, division

import os
import json

import xl_auth


def test_package_name_is_xl_auth():
    assert xl_auth.__name__ == 'xl_auth'


def test_package_version_matches_package_json():
    with open(os.path.join(os.path.dirname(__file__), '..', 'package.json')) as package_json:
        assert xl_auth.__version__ == json.load(package_json)['version']
