# -*- coding: utf-8 -*-
"""
    :py:mod:`~tests.scripts_tests`
    ==============================

    Second tests module! :) Now targeting setuptools entrypoints.


    ----

    .. versionadded:: 0.1
"""

from __future__ import (
    print_function, absolute_import, unicode_literals, division)

from testfixtures import OutputCapture

from . import XlAuthTestCase

from xl_auth import scripts


__all__ = ['ScriptsTestCase']


class ScriptsTestCase(XlAuthTestCase):
    """Tests' module for :py:mod:`~xl_auth.scripts` module entrypoints."""

    # noinspection PyMethodMayBeStatic
    def test_ping_entrypoint_prints_pong(self):  # noqa
        with OutputCapture() as output:
            scripts.say_pong()

        output.compare('pong')
