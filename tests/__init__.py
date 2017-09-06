# -*- coding: utf-8 -*-
"""
    :py:mod:`tests` -- Root Tests Package
    ====================================

    Tests package! :)


    ----

    .. moduleauthor:: Mats Blomdahl <mats.blomdahl@gmail.com>

    .. versionadded:: 0.1
"""

from __future__ import print_function, absolute_import, unicode_literals, division

from unittest import TestCase


__all__ = ['XlAuthTestCase']


class XlAuthTestCase(TestCase):
    """Base class for :py:mod:`xl_auth` test cases."""

    def setUp(self):  # noqa
        super(XlAuthTestCase, self).setUp()

    def tearDown(self):  # noqa
        super(XlAuthTestCase, self).tearDown()
