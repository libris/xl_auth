# -*- coding: utf-8 -*-
"""Click commands."""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
from glob import glob
from subprocess import call

import click
from flask import current_app
from flask.cli import with_appcontext
from werkzeug.exceptions import MethodNotAllowed, NotFound

from xl_auth.user.models import User

# Disable warnings on discouraged Py3 use (http://click.pocoo.org/python3/).
click.disable_unicode_literals_warning = True

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
@click.option('-j', '--junit-xml', help='create JUnit XML output at given path')
def test(junit_xml=None):
    """Run the tests."""
    import pytest
    args = [TEST_PATH, '--verbose']
    if junit_xml:
        args.append('--junit-xml={}'.format(junit_xml))
    rv = pytest.main(args)
    exit(rv)


@click.command()
@click.option('-f', '--fix-imports', default=False, is_flag=True,
              help='Fix imports using isort, before linting')
def lint(fix_imports):
    """Lint and check code style with flake8/isort."""
    skip = ['node_modules', 'venv', 'py27venv', 'py35venv', 'py36venv', 'requirements']
    root_files = glob('*.py')
    root_directories = [
        name for name in next(os.walk('.'))[1] if not name.startswith('.')]
    files_and_directories = [
        arg for arg in root_files + root_directories if arg not in skip]

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo('{}: {}'.format(description, ' '.join(command_line)))
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    if fix_imports:
        execute_tool('Fixing import order', 'isort', '-rc')
    execute_tool('Checking code style', 'flake8')


@click.command()
@click.option('-c', '--compile-only', default=False, is_flag=True, help='Only run compile step.')
@with_appcontext
def translate(compile_only):
    """Run pybabel extract/update/compile."""
    from sh import Command
    pybabel = Command('pybabel')

    if not compile_only:
        click.echo(pybabel(
            '-v', 'extract', '--width', '100', '--mapping-file', 'babel.cfg',
            '--copyright-holder', current_app.config['APP_AUTHOR'],
            '--project', current_app.config['APP_NAME'],
            '--version', current_app.config['APP_VERSION'],
            '--output-file', 'messages.pot', '.').stderr)
        click.echo(pybabel(
            '-v', 'update', '--width', '100', '--input-file', 'messages.pot', '--output-dir',
            'xl_auth/translations/').stderr)

    click.echo(pybabel(
        '-v', 'compile', '--statistics', '--directory', 'xl_auth/translations/').stderr)


@click.command()
def clean():
    """Remove *.pyc and *.pyo files in xl_auth.

    Borrowed from Flask-Script, converted to use Click.
    """
    for dirpath, dirnames, filenames in os.walk('xl_auth'):
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                full_pathname = os.path.join(dirpath, filename)
                click.echo('Removing {}'.format(full_pathname))
                os.remove(full_pathname)


@click.command()
@click.option('--email', required=True, default=None, help='Email for user')
@click.option('--full-name', default=None, help='Full name for user (default: None)')
@click.option('--password', default='password', help='Password for user (default: password)')
@click.option('--active', default=True, is_flag=True, help='Activate account (default: True)')
@click.option('--is-admin', default=False, is_flag=True, help='Create admin user (default: False)')
@with_appcontext
def create_user(email, full_name, password, active, is_admin):
    """Create user account."""
    full_name = full_name or email
    user = User.create(email=email, full_name=full_name, password=password,
                       active=active, is_admin=is_admin)
    click.echo('Created account with login {0}'.format(user.email))


@click.command()
@click.option('--url', default=None, help='Url to test (ex. /static/image.png)')
@click.option('--order', default='rule', help='Property on Rule to order by (default: rule)')
@with_appcontext
def urls(url, order):
    """Display the url matching routes for xl_auth.

    Borrowed from Flask-Script, converted to use Click.
    """
    rows = []
    column_length = 0
    column_headers = ('Rule', 'Endpoint', 'Arguments')

    if url:
        try:
            rule, arguments = (
                current_app.url_map
                           .bind('localhost')
                           .match(url, return_rule=True))
            rows.append((rule.rule, rule.endpoint, arguments))
            column_length = 3
        except (NotFound, MethodNotAllowed) as e:
            rows.append(('<{}>'.format(e), None, None))
            column_length = 1
    else:
        rules = sorted(
            current_app.url_map.iter_rules(),
            key=lambda rule: getattr(rule, order))
        for rule in rules:
            rows.append((rule.rule, rule.endpoint, None))
        column_length = 2

    str_template = ''
    table_width = 0

    if column_length >= 1:
        max_rule_length = max(len(r[0]) for r in rows)
        max_rule_length = max_rule_length if max_rule_length > 4 else 4
        str_template += '{:' + str(max_rule_length) + '}'
        table_width += max_rule_length

    if column_length >= 2:
        max_endpoint_length = max(len(str(r[1])) for r in rows)
        # max_endpoint_length = max(rows, key=len)
        max_endpoint_length = (
            max_endpoint_length if max_endpoint_length > 8 else 8)
        str_template += '  {:' + str(max_endpoint_length) + '}'
        table_width += 2 + max_endpoint_length

    if column_length >= 3:
        max_arguments_length = max(len(str(r[2])) for r in rows)
        max_arguments_length = (
            max_arguments_length if max_arguments_length > 9 else 9)
        str_template += '  {:' + str(max_arguments_length) + '}'
        table_width += 2 + max_arguments_length

    click.echo(str_template.format(*column_headers[:column_length]))
    click.echo('-' * table_width)

    for row in rows:
        click.echo(str_template.format(*row[:column_length]))
