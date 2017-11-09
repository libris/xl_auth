# -*- coding: utf-8 -*-
"""Test client forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice

import pytest
from flask_babel import gettext as _
from wtforms.validators import ValidationError

from xl_auth.oauth.client.forms import EditForm, RegisterForm


def test_user_cannot_register_client(user):
    """Attempt to register a client as regular user."""
    form = RegisterForm(user, name='Client',
                        description='OAuth2 Client',
                        is_confidential=choice([True, False]),
                        redirect_uris='http://localhost/',
                        default_scopes='read write')

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert e_info.value.args[0] == _('You do not have sufficient privileges for this operation.')


def test_register_form_validate_success(superuser):
    """Register client."""
    form = RegisterForm(superuser, name='Client',
                        description='OAuth2 Client',
                        is_confidential=choice([True, False]),
                        redirect_uris='http://localhost/',
                        default_scopes='read write')

    assert form.validate() is True


def test_register_form_missing_name(superuser):
    """Attempt to register client with missing name."""
    form = RegisterForm(superuser,
                        description='OAuth2 Client',
                        is_confidential=choice([True, False]),
                        redirect_uris='http://localhost/',
                        default_scopes='read write')

    assert form.validate() is False
    assert _('This field is required.') in form.name.errors


def test_register_form_too_short_name(superuser):
    """Attempt to register client with too short name."""
    form = RegisterForm(superuser, name='C',
                        description='OAuth2 Client',
                        is_confidential=choice([True, False]),
                        redirect_uris='http://localhost/',
                        default_scopes='read write')

    assert form.validate() is False
    assert _('Field must be between 3 and 64 characters long.') in form.name.errors


def test_register_form_missing_description(superuser):
    """Attempt to register client with missing description."""
    form = RegisterForm(superuser, name='Client',
                        is_confidential=choice([True, False]),
                        redirect_uris='http://localhost/',
                        default_scopes='read write')

    assert form.validate() is False
    assert _('This field is required.') in form.description.errors


def test_register_form_too_short_description(superuser):
    """Attempt to register client with too short description."""
    form = RegisterForm(superuser, name='Client',
                        description='C',
                        is_confidential=choice([True, False]),
                        redirect_uris='http://localhost/',
                        default_scopes='read write')

    assert form.validate() is False
    assert _('Field must be between 3 and 350 characters long.') in form.description.errors


def test_register_form_missing_redirect_uris(superuser):
    """Attempt to register client with missing redirect URIs."""
    form = RegisterForm(superuser, name='Client',
                        description='OAuth2 Client',
                        is_confidential=choice([True, False]),
                        default_scopes='read write')

    assert form.validate() is False
    assert _('This field is required.') in form.redirect_uris.errors


def test_register_form_missing_default_scopes(superuser):
    """Attempt to register client with missing default scopes."""
    form = RegisterForm(superuser, name='Client',
                        description='OAuth2 Client',
                        is_confidential=choice([True, False]),
                        redirect_uris='http://localhost/')

    assert form.validate() is False
    assert _('This field is required.') in form.default_scopes.errors


def test_user_cannot_edit_collection(user, client):
    """Attempt to edit a client as regular user."""
    form = EditForm(user, name=client.name,
                    description=client.description,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert e_info.value.args[0] == _('You do not have sufficient privileges for this operation.')


def test_edit_form_validate_success(superuser, client):
    """Edit entry with success."""
    form = EditForm(superuser, name=client.name,
                    description=client.description,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is True


def test_edit_form_missing_name(superuser, client):
    """Attempt to register client with missing name."""
    form = EditForm(superuser,
                    description=client.description,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is False
    assert _('This field is required.') in form.name.errors


def test_edit_form_too_short_name(superuser, client):
    """Attempt to register client with too short name."""
    form = EditForm(superuser, name='C',
                    description=client.description,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is False
    assert _('Field must be between 3 and 64 characters long.') in form.name.errors


def test_edit_form_missing_description(superuser, client):
    """Attempt to register client with missing description."""
    form = EditForm(superuser, name=client.name,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is False
    assert _('This field is required.') in form.description.errors


def test_edit_form_too_short_description(superuser, client):
    """Attempt to register client with too short description."""
    form = EditForm(superuser, name=client.name,
                    description='C',
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is False
    assert _('Field must be between 3 and 350 characters long.') in form.description.errors


def test_edit_form_missing_redirect_uris(superuser, client):
    """Attempt to register client with missing redirect URIs."""
    form = EditForm(superuser, name=client.name,
                    description=client.description,
                    is_confidential=not client.is_confidential,
                    default_scopes='read write')

    assert form.validate() is False
    assert _('This field is required.') in form.redirect_uris.errors


def test_edit_form_missing_default_scopes(superuser, client):
    """Attempt to register client with missing default scopes."""
    form = EditForm(superuser, name=client.name,
                    description=client.description,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/')

    assert form.validate() is False
    assert _('This field is required.') in form.default_scopes.errors
