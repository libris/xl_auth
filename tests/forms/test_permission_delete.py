# -*- coding: utf-8 -*-
"""Test permission DeleteForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import gettext as _

from xl_auth.permission.forms import DeleteForm

from ..factories import PermissionFactory


def test_validate_permission_id_does_not_exist(superuser, permission):
    """Attempt deleting permissions with a permission ID that does not exist."""
    invalid_permission_id = permission.id + 256
    form = DeleteForm(superuser, invalid_permission_id, permission_id=invalid_permission_id,
                      acknowledged='y')

    assert form.validate() is False
    assert _('Permission ID "%(permission_id)s" does not exist',
             permission_id=invalid_permission_id) in form.permission_id.errors


def test_validate_inconsistent_permission_id(permission):
    """Attempt deleting permission with inconsistent 'permission_id'."""
    other_permission = PermissionFactory().save_as(permission.user)
    form = DeleteForm(permission.user, permission.id, permission_id=other_permission.id,
                      acknowledged='y')

    assert form.validate() is False
    assert _('Invalid value, must be one of: %(values)s.', values=permission.id) in \
        form.permission_id.errors


def test_validate_when_acknowledged_is_not_y(permission):
    """Attempt deleting permission with 'acknowledged' set to e.g. 'no'."""
    form = DeleteForm(permission.user, permission.id, permission_id=permission.id,
                      acknowledged='no')

    assert form.validate() is False
    assert _('Invalid value, must be one of: %(values)s.', values='y') in form.acknowledged.errors


def test_validate_permission_edit_as_user(user, permission):
    """Attempt to edit entry as user that's not cataloging admin."""
    assert user.is_cataloging_admin is False
    form = DeleteForm(user, permission.id, permission_id=permission.id, acknowledged='y')

    assert form.validate() is False
    assert _('You do not have sufficient privileges for this operation.') in \
        form.permission_id.errors


def test_validate_success_as_cataloging_admin(user, permission):
    """Delete entry with success as cataloging admin."""
    # Make user cataloging admin.
    PermissionFactory(user=user, collection=permission.collection,
                      cataloging_admin=True).save_as(user)
    assert user.is_cataloging_admin_for(permission.collection) is True
    form = DeleteForm(user, permission.id, permission_id=permission.id, acknowledged='y')

    assert form.validate() is True
    assert form.data == {
        'permission_id': permission.id,
        'acknowledged': 'y',
        'next_redirect': None
    }


def test_validate_success_as_superuser(superuser, permission):
    """Delete entry with success as superuser."""
    form = DeleteForm(superuser, permission.id, permission_id=permission.id, acknowledged='y')

    assert form.validate() is True
    assert form.data == {
        'permission_id': permission.id,
        'acknowledged': 'y',
        'next_redirect': None
    }
