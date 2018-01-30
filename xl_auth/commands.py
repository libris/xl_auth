# -*- coding: utf-8 -*-
"""Click commands."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
import json
import os
from copy import deepcopy
from glob import glob
from os import execlp
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
@click.option('-e', '--email', required=True, default=None, help='Email for user')
@click.option('-n', '--full-name', default=None, help='Full name for user (default: None)')
@click.option('-p', '--password', default=None, help='Password for user (default: None)')
@click.option('--admin-email', default='libris@kb.se', help='Related admin (default: None)')
@click.option('--is-active', default=False, is_flag=True, help='Activate account (default: False)')
@click.option('--is-admin', default=False, is_flag=True, help='Create admin user (default: False)')
@click.option('-f', '--force', default=False, is_flag=True,
              help='Force overwrite existing account (default: False)')
@with_appcontext
def create_user(email, full_name, password, admin_email, is_active, is_admin, force):
    """Create or overwrite user account."""
    user = User.get_by_email(email)
    op_admin = User.get_by_email(admin_email)
    if force and user:
        if full_name:
            user.full_name = full_name
        user.set_password(password)
        user.update(is_active=is_active, is_admin=is_admin)
        user.save_as(op_admin)
        click.echo('Overwritten account with login {0}:{1}'.format(user.email, password))
    else:
        user = User.create_as(op_admin,
                              email=email, full_name=full_name or email, password=password,
                              is_active=is_active, is_admin=is_admin)
        click.echo('Created account with login {0}:{1}'.format(user.email, password))


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
            rule, arguments = current_app.url_map.bind('localhost').match(url, return_rule=True)
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


@click.command()
@click.option('-v', '--verbose', default=False, is_flag=True, help='Increase verbosity')
@click.option('--admin-email', required=True, default=None, help='Email for admin')
@click.option('--wipe-permissions', default=False, is_flag=True, help='Wipe outdated permissions')
@click.option('--send-password-resets', default=False, is_flag=True,
              help='Email password resets to new users')
@with_appcontext
def import_data(verbose, admin_email, wipe_permissions, send_password_resets):
    """Read data from Voyager dump and BibDB API to create DB entities.

    Creates:
        - collections
        - user accounts for collection managers
        - permissions between the two

    """
    import requests
    from flask_babel import gettext

    from .collection.forms import RegisterForm as CollectionRegisterForm
    from .collection.models import Collection
    from .permission.models import Permission
    from .user.forms import RegisterForm as UserRegisterForm
    from .user.models import PasswordReset, User

    def _get_collection_details_from_bibdb(code):
        raw_bibdb_api_data = json.loads(requests.get(
            'https://bibdb.libris.kb.se/api/lib?level=brief&sigel={}'
            .format(code)).content.decode('utf-8'))
        if raw_bibdb_api_data['query']['operation'] == 'sigel {}'.format(code):
            if verbose:
                print('Fetched details for sigel %r' % code)
            else:
                click.echo('.', nl=False)
        else:
            if not verbose:
                click.echo('x', nl=False)
            raise AssertionError('Lookup failed for sigel %r' % code)

        bibdb_api_data = None
        for chunk in raw_bibdb_api_data['libraries']:
            if chunk['sigel'] == code:
                if bibdb_api_data is not None:
                    raise AssertionError('Duplicate results for sigel %r' % code)
                bibdb_api_data = chunk
        if not bibdb_api_data:
            raise AssertionError('Zero results for sigel %r' % code)

        if bibdb_api_data['type'] in {'library', 'bibliography'}:
            category = bibdb_api_data['type']
        else:
            category = 'uncategorized'

        if bibdb_api_data['dept']:
            friendly_name = '%s, %s' % (bibdb_api_data['name'], bibdb_api_data['dept'])
        else:
            friendly_name = bibdb_api_data['name']

        assert bibdb_api_data['alive'] in {True, False}

        collection = {
            'friendly_name': friendly_name,
            'code': bibdb_api_data['sigel'],
            'category': category,
            'is_active': bibdb_api_data['alive'],
            'replaces': bibdb_api_data['sigel_old'],
            'replaced_by': bibdb_api_data['sigel_new']
        }

        if bibdb_api_data['date_created']:
            collection['created_at'] = \
                dt.datetime.strptime(bibdb_api_data['date_created'], '%Y-%m-%dT%H:%M:%S')

        return collection

    def _get_voyager_data():
        raw_voyager_sigels_and_locations = requests.get(
            'https://github.com/libris/xl_auth/files/1513982/171129_KB--sigel_locations.txt'
        ).content.decode('latin-1').splitlines()
        voyager_sigels_and_collections = dict()
        voyager_main_sigels, voyager_location_sigels = set(), set()
        for voyager_row in raw_voyager_sigels_and_locations:
            voyager_sigel, voyager_location = voyager_row.split(',')
            assert voyager_sigel and voyager_location
            voyager_main_sigels.add(voyager_sigel)
            voyager_location_sigels.add(voyager_location)
            if voyager_sigel == 'SEK' and voyager_location != 'SEK':
                continue  # Don't add all the collections under SEK super cataloger.
            if voyager_sigel in voyager_sigels_and_collections:
                voyager_sigels_and_collections[voyager_sigel].add(voyager_location)
            else:
                voyager_sigels_and_collections[voyager_sigel] = {voyager_location}
        print('voyager_main_sigels:', len(voyager_main_sigels), '/',
              'voyager_location_sigels:', len(voyager_location_sigels))
        print('(voyager_main_sigels | voyager_location_sigels):',
              len(voyager_main_sigels | voyager_location_sigels))

        return {
            'sigel_to_collections': voyager_sigels_and_collections,
            'sigels': voyager_main_sigels,
            'collections': voyager_location_sigels
        }

    def _get_bibdb_cataloging_admins():
        raw_bibdb_sigels_and_cataloging_admins = requests.get(
            'https://libris.kb.se/libinfo/library_konreg.jsp').content.decode('utf-8').splitlines()

        registering_bibdb_sigels, bibdb_cataloging_admins = set(), set()
        bibdb_sigels_and_cataloging_admins = dict()
        bibdb_cataloging_admins_and_sigels = dict()
        bibdb_cataloging_admin_emails_and_names = dict()
        for bibdb_row in raw_bibdb_sigels_and_cataloging_admins:
            try:
                bibdb_sigel, cataloging_admin_name, cataloging_admin_email = bibdb_row.split(',')
            except ValueError as err:
                print('ValueError: %s / bibdb_row: %r' % (err, bibdb_row))
                continue
            cataloging_admin_email = cataloging_admin_email.lower()
            bibdb_cataloging_admin_emails_and_names[cataloging_admin_email] = cataloging_admin_name
            assert bibdb_sigel != ''
            registering_bibdb_sigels.add(bibdb_sigel)
            if not cataloging_admin_email:
                continue

            bibdb_cataloging_admins.add(cataloging_admin_email)
            bibdb_sigels_and_cataloging_admins[bibdb_sigel] = cataloging_admin_email

            if cataloging_admin_email in bibdb_cataloging_admins_and_sigels:
                bibdb_cataloging_admins_and_sigels[cataloging_admin_email].add(bibdb_sigel)
            else:
                bibdb_cataloging_admins_and_sigels[cataloging_admin_email] = {bibdb_sigel}

        print('registering_bibdb_sigels:', len(registering_bibdb_sigels), '/',
              'bibdb_cataloging_admins:', len(bibdb_cataloging_admins))

        return {
            'sigel_to_cataloging_admins': bibdb_sigels_and_cataloging_admins,
            'cataloging_admin_to_sigels': bibdb_cataloging_admins_and_sigels,
            'cataloging_admin_emails_to_names': bibdb_cataloging_admin_emails_and_names,
            'sigels': registering_bibdb_sigels,
            'cataloging_admins': bibdb_cataloging_admins,
        }

    def _get_bibdb_sigels_not_in_voyager(bibdb_sigels, voyager_sigels):
        unknown_sigels = set()
        for bibdb_sigel in bibdb_sigels:
            if bibdb_sigel not in voyager_sigels:
                unknown_sigels.add(bibdb_sigel)
        return unknown_sigels

    def _generate_xl_auth_cataloging_admins_and_collections(bibdb_cataloging_admin_to_sigels,
                                                            voyager_sigel_to_collections):
        pre_total, post_total = 0, 0
        voyager_sigels_unknown_in_bibdb = set()
        xl_auth_cataloging_admins = dict()
        xl_auth_collections = dict()
        # Prepare permissions for cataloging admins.
        for cataloging_admin, sigels in bibdb_cataloging_admin_to_sigels.items():
            pre_total += len(sigels)
            xl_auth_cataloging_admins[cataloging_admin] = set()
            for sigel in sigels:
                # Fetch details if necessary.
                if sigel not in xl_auth_collections:
                    xl_auth_collections[sigel] = _get_collection_details_from_bibdb(sigel)

                xl_auth_cataloging_admins[cataloging_admin].add(sigel)

                if sigel in bibdb_sigels_unknown_in_voyager:
                    continue  # Don't attempt resolving sigels that does not exist in Voyager.

                # Add additional sigels from Voyager sigel-to-"sub-sigel" mapping.
                for voyager_collection in voyager_sigel_to_collections[sigel]:
                    if voyager_collection not in xl_auth_collections:
                        try:
                            # Fetch details if necessary.
                            xl_auth_collections[voyager_collection] = \
                                _get_collection_details_from_bibdb(voyager_collection)
                        except AssertionError as err:
                            voyager_sigels_unknown_in_bibdb.add(voyager_collection)
                            if verbose:
                                print(err)
                            continue
                    xl_auth_cataloging_admins[cataloging_admin].add(voyager_collection)

            post_total += len(xl_auth_cataloging_admins[cataloging_admin])

        print('\npre_total:', pre_total, '/ post_total:', post_total)
        print('voyager_sigels_unknown_in_bibdb:', voyager_sigels_unknown_in_bibdb)

        resolved_bibdb_refs = set()
        unresolved_bibdb_refs = set()
        print('before-replaces-lookups:', len(xl_auth_collections))
        for _ in range(10):
            for _, details in deepcopy(xl_auth_collections).items():
                for old_new_ref in {'replaces', 'replaced_by'}:
                    if details[old_new_ref] and details[old_new_ref] not in xl_auth_collections:
                        try:
                            xl_auth_collections[details[old_new_ref]] = \
                                _get_collection_details_from_bibdb(details[old_new_ref])
                            resolved_bibdb_refs.add(details[old_new_ref])
                        except AssertionError as err:
                            unresolved_bibdb_refs.add(details[old_new_ref])
                            print(err)
        print('after-replaces-lookups:', len(xl_auth_collections))

        print('resolved_bibdb_refs:', resolved_bibdb_refs)
        print('unresolved_bibdb_refs:', unresolved_bibdb_refs)

        return {
            'collections': xl_auth_collections,
            'cataloging_admins': xl_auth_cataloging_admins
        }

    def _get_manually_added_permissions():
        emails_and_collection_codes = requests.get(
            'https://docs.google.com/spreadsheets/d/e/2PACX-1vT2TjS_L9_J5LJztfKWo0UxQD-RCZo3bheFIH'
            'Ouz2Gu-aGcd7IrlDzHDmQ2yL726z0BnSc47vasL0l3/pub?gid=0&single=true&output=tsv'
        ).content.decode('utf-8').splitlines()

        manual_additions = []
        for add_row in emails_and_collection_codes[1:]:
            add_email, add_code, _ = add_row.split('\t')
            manual_additions.append((add_email.strip(), add_code.strip()))

        return manual_additions

    def _get_manually_deleted_permissions():
        emails_and_collection_codes = requests.get(
            'https://docs.google.com/spreadsheets/d/e/2PACX-1vT2TjS_L9_J5LJztfKWo0UxQD-RCZo3bheFIH'
            'Ouz2Gu-aGcd7IrlDzHDmQ2yL726z0BnSc47vasL0l3/pub?gid=518641812&single=true&output=tsv'
        ).content.decode('utf-8').splitlines()

        manual_deletions = []
        for del_row in emails_and_collection_codes[1:]:
            del_email, del_code, _ = del_row.split('\t')
            manual_deletions.append((del_email.strip(), del_code.strip()))

        return manual_deletions

    # Get admin user
    admin = User.get_by_email(admin_email)

    # Gather data.
    voyager = _get_voyager_data()
    bibdb = _get_bibdb_cataloging_admins()

    bibdb_sigels_unknown_in_voyager = \
        _get_bibdb_sigels_not_in_voyager(bibdb['sigels'], voyager['sigels'])
    print('bibdb_sigels_unknown_in_voyager:', bibdb_sigels_unknown_in_voyager)

    # Compile it into xl_auth-compatible model.
    xl_auth = _generate_xl_auth_cataloging_admins_and_collections(
        bibdb['cataloging_admin_to_sigels'], voyager['sigel_to_collections'])

    # Store collections.
    for collection, details in deepcopy(xl_auth['collections']).items():
        with current_app.test_request_context():
            collection_form = CollectionRegisterForm(admin, code=details['code'],
                                                     friendly_name=details['friendly_name'])
            collection_form.validate()
        if collection_form.code.errors or collection_form.friendly_name.errors:
            for code_error in collection_form.code.errors:
                print('collection %r: %s' % (collection, code_error))
            for friendly_name_error in collection_form.friendly_name.errors:
                print('friendly_name %r: %s' % (details['friendly_name'], friendly_name_error))
            del xl_auth['collections'][collection]
            continue

        collection = Collection.get_by_code(code=details['code'])
        if collection:
            if collection.is_active != details['is_active']:
                collection.is_active = details['is_active']
                collection.save_as(admin)
                print('corrected collection %r: is_active=%s'
                      % (collection.code, collection.is_active))
        else:
            collection = Collection(**details)
            if collection.created_at:
                collection.modified_at = collection.created_at
                collection.modified_by = collection.created_by = admin
                collection.save(preserve_modified=True)
            else:
                collection.save_as(admin)

    # Store users.
    for email, full_name in deepcopy(bibdb['cataloging_admin_emails_to_names']).items():
        if email not in bibdb['cataloging_admins']:
            del bibdb['cataloging_admin_emails_to_names'][email]
            continue

        with current_app.test_request_context():
            user_form = UserRegisterForm(None, username=email, full_name=full_name)
            user_form.validate()
        if gettext('Email already registered') in user_form.username.errors:
            pass
        elif user_form.username.errors or user_form.full_name.errors:
            print('validation failed for %s <%s>' % (full_name, email))
            for username_error in user_form.username.errors:
                print('email %r: %s' % (email, username_error))
            for full_name_error in user_form.full_name.errors:
                print('full_name %r: %s' % (full_name, full_name_error))
            del bibdb['cataloging_admin_emails_to_names'][email]
            continue

        user = User.get_by_email(email)
        if not user:
            user = User(email=email, full_name=full_name, is_active=False)
            if send_password_resets:  # Requires SERVER_NAME and PREFERRED_URL_SCHEME env vars.
                with current_app.test_request_context():
                    password_reset = PasswordReset(user)
                    password_reset.send_email(account_registration_from_user=admin)
                    user.save_as(admin)
                    password_reset.save()
                print('Added inactive user %r (password reset email sent).' % email)
            else:
                user.save_as(admin)
                print('Added inactive user %r (no password reset).' % email)

    old_permissions = Permission.query.all()
    current_permissions, new_permissions, removed_permissions = [], [], []

    # Store permissions.
    for email, collections in xl_auth['cataloging_admins'].items():
        user = User.get_by_email(email)
        if not user:
            continue

        for code in collections:
            collection = Collection.get_by_code(code)
            if not collection:
                print('Collection %r does not exist' % code)
                continue
            permission = Permission.query.filter_by(user_id=user.id,
                                                    collection_id=collection.id).first()
            if permission:
                current_permissions.append(permission)
            elif collection.is_active:  # No creating permissions on inactive collections.
                if user.email == 'test@kb.se':
                    permission = Permission.create_as(admin, user=user, collection=collection,
                                                      registrant=True,
                                                      cataloger=collection.code == 'Utb2',
                                                      cataloging_admin=False)
                else:
                    permission = Permission.create_as(admin, user=user, collection=collection,
                                                      registrant=True, cataloger=True,
                                                      cataloging_admin=True)
                new_permissions.append(permission)

    # Apply manual additions.
    for email, code in _get_manually_added_permissions():
        user = User.get_by_email(email)
        if not user:
            print('Cannot add permission manually; user %r does not exist' % email)
            continue

        collection = Collection.get_by_code(code)
        if not collection:
            print('Cannot add permission manually, collection %r does not exist' % code)
            continue

        permission = Permission.query.filter_by(user_id=user.id,
                                                collection_id=collection.id).first()
        if permission:
            current_permissions.append(permission)
            if verbose:
                print('Manual permission for %r on %r already exists.' % (email, code))
        else:
            permission = Permission.create_as(admin, user=user, collection=collection,
                                              registrant=True, cataloger=True,
                                              cataloging_admin=True)
            new_permissions.append(permission)
            if verbose:
                print('Manually added permissions for %r on %r.' % (email, code))

    # Apply manual deletions.
    for email, code in _get_manually_deleted_permissions():
        user = User.get_by_email(email)
        if not user:
            print('Cannot delete permission manually; user %r does not exist' % email)
            continue

        collection = Collection.get_by_code(code)
        if not collection:
            print('Cannot delete permission manually, collection %r does not exist' % code)
            continue

        permission = Permission.query.filter_by(user_id=user.id,
                                                collection_id=collection.id).first()
        if permission:
            permission.delete()
            removed_permissions.append(permission)
            if verbose:
                print('Manually deleted permissions for %r on %r.' % (email, code))
        else:
            current_permissions.append(permission)
            if verbose:
                print('Cannot manually deleted permissions for %r on %r; does not exist.'
                      % (email, code))

    # Optionally wipe permissions not deduced from controlled sources (BibDB, Voyager, manual),
    # but only if created by admin account. And also existing permissions on inactive collections.
    for permission in old_permissions:
        if not permission.collection.is_active:
            print('Existing permission for %r on inactive collection %r (deleting=%s).'
                  % (permission.user.email, permission.collection.code, wipe_permissions))
            if wipe_permissions:
                permission.delete()
            continue
        elif permission in current_permissions and permission not in removed_permissions:
            continue
        else:
            if permission.created_by != admin:
                print('Unknown permission for %r on %r, created by %r (deleting=False).'
                      % (permission.user.email, permission.collection.code,
                         permission.created_by.email))
                continue

            print('Permission for %r on %r not found during import (deleting=%s).'
                  % (permission.user.email, permission.collection.code, wipe_permissions))
            if wipe_permissions:
                permission.delete()


@click.command()
def prod_run():
    """Run application with production setup."""
    execlp('gunicorn', 'gunicorn', '-c', 'gunicorn_conf.py', 'autoapp:app')
