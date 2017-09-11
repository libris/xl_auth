# -*- coding: utf-8 -*-
"""
    :py:mod:`~xl_auth.factory` -- WSGI Application Factory
    ======================================================

    Factory module for creating the :py:class:`~flask.Flask` WSGI application.


    ----

    .. versionadded:: 0.1
"""

from __future__ import print_function, absolute_import, unicode_literals, division

from flask import Flask

from . import __name__ as package_name


__all__ = ['create_app']


def create_app(application_name=package_name):
    """Create a *xl_auth* :py:class:`~flask.Flask` WSGI application.

    :param unicode application_name: Name identifying the app (optional,
                                     defaults to package name).

    :returns: A :py:class:`~flask.Flask` WSGI application.
    """

    return Flask(application_name)
