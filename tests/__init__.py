# -*- coding: utf-8 -*-
"""
    :py:mod:`tests` -- Root Tests Package
    =====================================

    Tests package! :)


    ----

    .. versionadded:: 0.1
"""

from __future__ import (
    print_function, absolute_import, unicode_literals, division)

from unittest import TestCase

from xl_auth import factory


__all__ = ['XlAuthTestCase']


class XlAuthTestCase(TestCase):
    """Base class for :py:mod:`xl_auth` test cases."""

    def setUp(self):  # noqa
        super(XlAuthTestCase, self).setUp()

        self.wsgi_app = factory.create_app(application_name='tests')
        if self.wsgi_app:
            self.client = self.wsgi_app.test_client(use_cookies=False)
            self.app_context = self.wsgi_app.app_context()
            self.app_context.push()

    def tearDown(self):  # noqa
        super(XlAuthTestCase, self).tearDown()

        if self.app_context:
            self.app_context.pop()
