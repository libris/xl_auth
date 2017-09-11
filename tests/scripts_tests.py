# -*- coding: utf-8 -*-
"""
    :py:mod:`~tests.scripts_tests`
    ==============================

    Second tests module! :) Now targeting setuptools entrypoints.


    ----

    .. versionadded:: 0.1
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from testfixtures import OutputCapture

from xl_auth import scripts

from . import XlAuthTestCase

__all__ = ['ScriptsTestCase']


class ScriptsTestCase(XlAuthTestCase):
    """Tests' module for :py:mod:`~xl_auth.scripts` module entrypoints."""

    # noinspection PyMethodMayBeStatic
    def test_ping_entrypoint_prints_pong(self):  # noqa
        with OutputCapture() as output:
            scripts.say_pong()

        output.compare('pong')
