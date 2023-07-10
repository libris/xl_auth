"""Test client EditForm."""


import pytest
from flask_babel import gettext as _
from wtforms.validators import ValidationError

from xl_auth.oauth.client.forms import EditForm


def test_user_cannot_edit_client(user, client):
    """Attempt to edit a client as regular user."""
    form = EditForm(user, name=client.name,
                    description=client.description,
                    user_id=-1,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert e_info.value.args[0] == _('You do not have sufficient privileges for this operation.')


def test_validate_success(superuser, client):
    """Edit entry with success."""
    form = EditForm(superuser, name=client.name,
                    description=client.description,
                    user_id=-1,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is True


def test_validate_success_with_user_id(superuser, user, client):
    """Edit entry with user_id with success."""
    form = EditForm(superuser, name=client.name,
                    description=client.description,
                    user_id=user.id,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is True


def test_invalid_user_id(superuser, client):
    """Attempt to edit client with invalid user_id."""
    bad_user_id = 42000000
    form = EditForm(superuser, name=client.name,
                    description=client.description,
                    user_id=bad_user_id,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is False
    assert _('User ID "%(user_id)s" does not exist', user_id=bad_user_id) in form.user_id.errors


def test_missing_name(superuser, client):
    """Attempt to register client with missing name."""
    form = EditForm(superuser,
                    description=client.description,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is False
    assert _('This field is required.') in form.name.errors


def test_too_short_name(superuser, client):
    """Attempt to register client with too short name."""
    form = EditForm(superuser, name='C',
                    description=client.description,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is False
    assert _('Field must be between 3 and 64 characters long.') in form.name.errors


def test_missing_description(superuser, client):
    """Attempt to register client with missing description."""
    form = EditForm(superuser, name=client.name,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is False
    assert _('This field is required.') in form.description.errors


def test_too_short_description(superuser, client):
    """Attempt to register client with too short description."""
    form = EditForm(superuser, name=client.name,
                    description='C',
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/',
                    default_scopes='read write')

    assert form.validate() is False
    assert _('Field must be between 3 and 350 characters long.') in form.description.errors


def test_missing_redirect_uris(superuser, client):
    """Attempt to register client with missing redirect URIs."""
    form = EditForm(superuser, name=client.name,
                    description=client.description,
                    is_confidential=not client.is_confidential,
                    default_scopes='read write')

    assert form.validate() is False
    assert _('This field is required.') in form.redirect_uris.errors


def test_missing_default_scopes(superuser, client):
    """Attempt to register client with missing default scopes."""
    form = EditForm(superuser, name=client.name,
                    description=client.description,
                    is_confidential=not client.is_confidential,
                    redirect_uris='http://localhost/')

    assert form.validate() is False
    assert _('This field is required.') in form.default_scopes.errors
