# -*- coding: utf-8 -*-
"""Test permission EditForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import gettext as _

from xl_auth.permission.forms import EditForm

from ..factories import CollectionFactory, PermissionFactory, UserFactory


def test_validate_permission_id_does_not_exist(superuser, permission):
    """Attempt editing permissions with a permission ID that does not exist."""
    invalid_permission_id = permission.id + 256
    form = EditForm(superuser, invalid_permission_id, permission_id=invalid_permission_id,
                    user_id=permission.user.id, collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('Permission ID "%(permission_id)s" does not exist',
             permission_id=invalid_permission_id) in form.permission_id.errors


def test_validate_inconsistent_permission_id(permission, superuser):
    """Attempt editing permission with inconsistent 'permission_id'."""
    other_permission = PermissionFactory().save_as(superuser)
    form = EditForm(permission.user, permission.id, permission_id=other_permission.id)

    assert form.validate() is False
    assert _('Invalid value, must be one of: %(values)s.', values=permission.id) in \
        form.permission_id.errors


def test_validate_with_placeholder_user_id(superuser, permission):
    """Attempt editing entry with the placeholder ID."""
    form = EditForm(superuser, permission.id, permission_id=permission.id,
                    user_id='-1', collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('A user must be selected.') in form.user_id.errors


def test_validate_without_user_id(superuser, permission):
    """Attempt editing entry with empty string for user ID."""
    form = EditForm(superuser, permission.id, permission_id=permission.id,
                    user_id='', collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('This field is required.') in form.user_id.errors


def test_validate_with_placeholder_collection_id(superuser, permission):
    """Attempt editing entry with the placeholder ID."""
    form = EditForm(superuser, permission.id, permission_id=permission.id,
                    user_id=permission.user.id, collection_id='-1')

    assert form.validate() is False
    assert _('A collection must be selected.') in form.collection_id.errors


def test_validate_without_collection_id(superuser, permission):
    """Attempt editing entry with empty string for collection ID."""
    form = EditForm(superuser, permission.id, permission_id=permission.id,
                    user_id=permission.user.id, collection_id='')

    assert form.validate() is False
    assert _('This field is required.') in form.collection_id.errors


def test_validate_permission_already_registered(superuser, permission):
    """Attempt editing permissions with a already registered (user_id, collection_id) pair."""
    other_permission = PermissionFactory()
    other_permission.save_as(superuser)
    form = EditForm(superuser, other_permission.id, permission_id=other_permission.id,
                    user_id=permission.user.id, collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('Permissions for user "%(username)s" on collection "%(code)s" already registered',
             username=permission.user.email, code=permission.collection.code
             ) in form.user_id.errors


def test_validate_user_id_does_not_exist(superuser, permission):
    """Attempt editing permissions by setting a user ID that does not exist."""
    invalid_user_id = permission.user.id + 500
    form = EditForm(superuser, permission.id, permission_id=permission.id, user_id=invalid_user_id,
                    collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('User ID "%(user_id)s" does not exist',
             user_id=invalid_user_id) in form.user_id.errors


def test_validate_collection_id_does_not_exist(superuser, permission):
    """Attempt editing permissions by setting a collection ID that does not exist."""
    invalid_collection_id = permission.user.id + 500
    form = EditForm(superuser, permission.id, permission_id=permission.id,
                    user_id=permission.user.id, collection_id=invalid_collection_id)

    assert form.validate() is False
    assert _('Collection ID "%(collection_id)s" does not exist',
             collection_id=invalid_collection_id) in form.collection_id.errors


def test_validate_permission_edit_as_user(permission, user, collection):
    """Attempt to edit entry as user that's not cataloging admin."""
    assert permission.user.id != user.id  # Existing permission maps to different user.
    assert permission.collection.id != collection.id  # And a different collection..
    form = EditForm(user, permission.id, permission_id=permission.id, user_id=user.id,
                    collection_id=collection.id, registrant=True, cataloger=True,
                    cataloging_admin=True)

    form.validate()
    assert _('You do not have sufficient privileges for this operation.') in \
        form.permission_id.errors


def test_validate_add_cataloging_admin_permission_as_cataloging_admin(user, permission, superuser):
    """Attempt to make another user cataloging admin being only cataloging admin yourself."""
    # Make 'user' cataloging admin for 'permission.collection'.
    PermissionFactory(user=user, collection=permission.collection,
                      cataloging_admin=True).save_as(superuser)
    assert user.is_cataloging_admin_for(permission.collection) is True
    # Make another user on the same collection that's not a cataloging admin.
    other_users_permission = PermissionFactory(collection=permission.collection,
                                               cataloging_admin=False).save_as(superuser)
    assert other_users_permission.user.is_cataloging_admin_for(permission.collection) is False
    form = EditForm(user, other_users_permission.id,
                    permission_id=other_users_permission.id,
                    user_id=other_users_permission.user.id,
                    collection_id=permission.collection.id,
                    cataloging_admin=True)

    assert form.validate() is False
    assert _('Cataloging admin rights can only be granted by system admins.') in \
        form.cataloging_admin.errors


def test_validate_success_as_cataloging_admin(user, permission, superuser):
    """Edit entry with success as cataloging admin."""
    # Make user cataloging admin for 'permission.collection' and 'other_collection'.
    PermissionFactory(user=user, collection=permission.collection,
                      cataloging_admin=True).save_as(superuser)
    other_collection = CollectionFactory().save_as(superuser)
    PermissionFactory(user=user, collection=other_collection,
                      cataloging_admin=True).save_as(superuser)
    other_user = UserFactory().save_as(user)
    assert user.is_cataloging_admin_for(permission.collection) is True
    form = EditForm(user, permission.id,
                    permission_id=permission.id,
                    user_id=other_user.id,
                    collection_id=other_collection.id,
                    cataloging_admin=permission.cataloging_admin,  # Must remain unchanged.
                    registrant=not permission.registrant,
                    cataloger=not permission.cataloger)

    assert form.validate() is True
    assert form.data == {
        'permission_id': permission.id,
        'user_id': other_user.id,
        'collection_id': other_collection.id,
        'registrant': not permission.registrant,
        'cataloger': not permission.cataloger,
        'cataloging_admin': permission.cataloging_admin,
        'next_redirect': None
    }


def test_validate_success_as_superuser(superuser, permission, user, collection):
    """Edit entry with success as superuser."""
    assert permission.user.id != user.id  # Existing permission maps to different user.
    assert permission.collection.id != collection.id  # And a different collection..
    form = EditForm(superuser, permission.id, permission_id=permission.id, user_id=user.id,
                    collection_id=collection.id, registrant=not permission.registrant,
                    cataloger=not permission.cataloger,
                    cataloging_admin=not permission.cataloging_admin)

    assert form.validate() is True
    assert form.data == {
        'permission_id': permission.id,
        'user_id': user.id,
        'collection_id': collection.id,
        'registrant': not permission.registrant,
        'cataloger': not permission.cataloger,
        'cataloging_admin': not permission.cataloging_admin,
        'next_redirect': None
    }
