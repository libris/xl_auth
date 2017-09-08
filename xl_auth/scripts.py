# -*- coding: utf-8 -*-
"""
    :py:mod:`~xl_auth.scripts`
    ==========================

    Module providing setuptools entry-point scripts.


    ----

    .. versionadded:: 0.1
"""

from __future__ import (
    print_function, absolute_import, unicode_literals, division)

from . import factory


__all__ = ['say_pong', 'run_wsgi']


def say_pong():
    print('pong')


def run_wsgi():
    app = factory.create_app()
    app.run()
