"""Gunicorn production config."""

from __future__ import absolute_import, division, print_function, unicode_literals

from click import echo

preload_app = True

bind = '0.0.0.0:5000'

#: See #175 for rationale.
worker_class = 'gthread'
workers = 4
threads = 2


def on_starting(_):
    """Master process initializing."""
    echo(_run_alembic_upgrade())


def on_reload(_):
    """Recycling workers due to SIGHUP."""
    echo(_run_alembic_upgrade())


def _run_alembic_upgrade():
    import sh
    from sh import Command
    try:
        flask_cmd = Command('flask')
        flask_cmd('db', 'upgrade')
    except sh.ErrorReturnCode as e:
        print(e.stderr)
