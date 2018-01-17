# -*- coding: utf-8 -*-
"""Gunicorn production config."""

from __future__ import absolute_import, division, print_function, unicode_literals

import multiprocessing

from click import echo

bind = '0.0.0.0:5000'

workers = multiprocessing.cpu_count() * 2 + 1


def on_starting(_):
    """Master process initializing."""
    echo(_run_alembic_upgrade())


def on_reload(_):
    """Recycling workers due to SIGHUP."""
    echo(_run_alembic_upgrade())


def _run_alembic_upgrade():
    from sh import Command
    flask_cmd = Command('flask')
    return flask_cmd('db', 'upgrade').stderr
