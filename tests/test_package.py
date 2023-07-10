"""Test :py:mod:`xl_auth` package identifiers."""

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import os

import xl_auth


def test_package_name_is_xl_auth():
    """Package name."""
    assert xl_auth.__name__ == 'xl_auth'


def test_package_version_matches_package_json():
    """Package version."""
    with open(os.path.join(os.path.dirname(__file__), '..', 'package.json')) as package_json:
        assert xl_auth.__version__ == json.load(package_json)['version']
