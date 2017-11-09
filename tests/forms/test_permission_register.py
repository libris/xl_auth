# -*- coding: utf-8 -*-
"""Test permission RegisterForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
from flask_babel import gettext as _
from wtforms.validators import ValidationError

from xl_auth.permission.forms import RegisterForm


def test_register_form_validate_without_user_id(superuser, collection):
    """Attempt registering entry with empty string for user ID."""
    form = RegisterForm(superuser, user_id='', collection_id=collection.id)

    assert form.validate() is False
    assert _('This field is required.') in form.user_id.errors


def test_register_form_validate_without_collection_id(superuser, user):
    """Attempt registering entry with empty string for collection ID."""
    form = RegisterForm(superuser, user_id=user.id, collection_id='')

    assert form.validate() is False
    assert _('This field is required.') in form.collection_id.errors


def test_register_form_validate_permission_already_registered(superuser, permission):
    """Attempt registering a (user_id, collection_id) mapping that is already registered."""
    form = RegisterForm(superuser, user_id=permission.user.id,
                        collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('Permissions for user "%(username)s" on collection "%(code)s" already registered',
             username=permission.user.email, code=permission.collection.code
             ) in form.user_id.errors


def test_register_form_validate_user_id_does_not_exist(superuser, user, collection):
    """Attempt registering a (user_id, collection_id) mapping where the user ID does not exist."""
    invalid_user_id = user.id + 500
    form = RegisterForm(superuser, user_id=invalid_user_id, collection_id=collection.id)

    assert form.validate() is False
    assert _('User ID "%(user_id)s" does not exist',
             user_id=invalid_user_id) in form.user_id.errors


def test_register_form_validate_collection_id_does_not_exist(superuser, user, collection):
    """Attempt registering a (user_id, collection_id) mapping where collection does not exist."""
    invalid_collection_id = collection.id + 500
    form = RegisterForm(superuser, user_id=user.id, collection_id=invalid_collection_id)

    assert form.validate() is False
    assert _('Collection ID "%(collection_id)s" does not exist',
             collection_id=invalid_collection_id) in form.collection_id.errors


def test_register_form_validate_success(superuser, user, collection):
    """Register new permission with success."""
    form = RegisterForm(superuser, user_id=user.id, collection_id=collection.id)

    assert form.validate() is True
    assert form.data == {
        'user_id': user.id,
        'collection_id': collection.id,
        'registrant': False,
        'cataloger': False,
        'cataloging_admin': False
    }


def test_register_form_as_user(user, collection):
    """Attempt to register new permission."""
    form = RegisterForm(user, user_id=user.id, collection_id=collection.id)

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert e_info.value.args[0] == _('You do not have sufficient privileges for this operation.')
