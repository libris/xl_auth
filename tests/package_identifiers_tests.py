# -*- coding: utf-8 -*-
"""
    :py:mod:`~tests.package_identifiers_tests`
    ==========================================

    First tests module! :)


    ----

    .. versionadded:: 0.1
"""

from __future__ import (
    print_function, absolute_import, unicode_literals, division)

from . import XlAuthTestCase

import xl_auth


__all__ = ['PackageIdentifiersTestCase']


class PackageIdentifiersTestCase(XlAuthTestCase):
    """Tests' module for :py:mod:`xl_auth` package identifiers."""

    def test_package_name_is_xl_auth(self):
        self.assertEqual(xl_auth.__name__, 'xl_auth')

    def test_package_version_is_0_1(self):
        self.assertEqual(xl_auth.__version__, '0.1')
