# -*- coding: utf-8 -*-
"""Test permission forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import gettext as _

from xl_auth.permission.forms import EditForm, RegisterForm

from ..factories import PermissionFactory


def test_edit_form_validate_permission_id_does_not_exist(permission):
    """Attempt editing permissions with a permission ID that does not exist."""
    invalid_permission_id = permission.id + 256
    form = EditForm(invalid_permission_id, user_id=permission.user.id,
                    collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('Permission ID "%(permission_id)s" does not exist',
             permission_id=invalid_permission_id) in form.permission_id.errors


def test_register_form_validate_without_user_id(collection):
    """Attempt registering entry with empty string for user ID."""
    form = RegisterForm(user_id='', collection_id=collection.id)

    assert form.validate() is False
    assert _('This field is required.') in form.user_id.errors


def test_edit_form_validate_without_user_id(permission):
    """Attempt editing entry with empty string for user ID."""
    form = EditForm(permission.id, user_id='', collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('This field is required.') in form.user_id.errors


def test_register_form_validate_without_collection_id(user):
    """Attempt registering entry with empty string for collection ID."""
    form = RegisterForm(user_id=user.id, collection_id='')

    assert form.validate() is False
    assert _('This field is required.') in form.collection_id.errors


def test_edit_form_validate_without_collection_id(permission):
    """Attempt editing entry with empty string for collection ID."""
    form = EditForm(permission.id, user_id=permission.user.id, collection_id='')

    assert form.validate() is False
    assert _('This field is required.') in form.collection_id.errors


def test_register_form_validate_permission_already_registered(permission):
    """Attempt registering a (user_id, collection_id) mapping that is already registered."""
    form = RegisterForm(user_id=permission.user.id, collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('Permissions for user ID "%(user_id)s" on collection ID "%(collection_id)s" already '
             'registered', user_id=permission.user.id, collection_id=permission.collection.id
             ) in form.user_id.errors


def test_edit_form_validate_permission_already_registered(permission):
    """Attempt editing permissions with a already registered (user_id, collection_id) pair."""
    other_permission = PermissionFactory()
    other_permission.save()
    form = EditForm(other_permission.id, user_id=permission.user.id,
                    collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('Permissions for user ID "%(user_id)s" on collection ID "%(collection_id)s" already '
             'registered', user_id=permission.user.id, collection_id=permission.collection.id
             ) in form.user_id.errors


def test_register_form_validate_user_id_does_not_exist(user, collection):
    """Attempt registering a (user_id, collection_id) mapping where the user ID does not exist."""
    invalid_user_id = user.id + 500
    form = RegisterForm(user_id=invalid_user_id, collection_id=collection.id)

    assert form.validate() is False
    assert _('User ID "%(user_id)s" does not exist',
             user_id=invalid_user_id) in form.user_id.errors


def test_edit_form_validate_user_id_does_not_exist(permission):
    """Attempt editing permissions by setting a user ID that does not exist."""
    invalid_user_id = permission.user.id + 500
    form = EditForm(permission.id, user_id=invalid_user_id, collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('User ID "%(user_id)s" does not exist',
             user_id=invalid_user_id) in form.user_id.errors


def test_register_form_validate_collection_id_does_not_exist(user, collection):
    """Attempt registering a (user_id, collection_id) mapping where collection does not exist."""
    invalid_collection_id = collection.id + 500
    form = RegisterForm(user_id=user.id, collection_id=invalid_collection_id)

    assert form.validate() is False
    assert _('Collection ID "%(collection_id)s" does not exist',
             collection_id=invalid_collection_id) in form.collection_id.errors


def test_edit_form_validate_collection_id_does_not_exist(permission):
    """Attempt editing permissions by setting a collection ID that does not exist."""
    invalid_collection_id = permission.user.id + 500
    form = EditForm(permission.id, user_id=permission.user.id, collection_id=invalid_collection_id)

    assert form.validate() is False
    assert _('Collection ID "%(collection_id)s" does not exist',
             collection_id=invalid_collection_id) in form.collection_id.errors


def test_register_form_validate_success(user, collection):
    """Register new permission with success."""
    form = RegisterForm(user_id=user.id, collection_id=collection.id)

    assert form.validate() is True
    assert form.data == {
        'user_id': user.id, 'collection_id': collection.id, 'register': False, 'catalogue': False}


def test_edit_form_validate_success(permission, user, collection):
    """Edit entry with success."""
    assert permission.user.id != user.id  # Existing permission maps to different user.
    assert permission.collection.id != collection.id  # And a different collection..
    form = EditForm(permission.id, user_id=user.id, collection_id=collection.id,
                    register=True, catalogue=True)

    assert form.validate() is True
    assert form.data == {
        'permission_id': permission.id,
        'user_id': user.id,
        'collection_id': collection.id,
        'register': True,
        'catalogue': True
    }
