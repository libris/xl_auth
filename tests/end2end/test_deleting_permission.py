# -*- coding: utf-8 -*-
"""Test deleting permissions."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import gettext as _

from xl_auth.permission.models import Permission


# noinspection PyUnusedLocal
def test_user_can_delete_existing_permission(user, permission, testapp):
    """Delete existing permission."""
    old_count = len(Permission.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Clicks Permissions button
    res = res.click(_('Permissions'))
    # Clicks Edit button on a permission
    res = res.click(_('Edit'))
    # Clicks Delete button on a permission
    permission_user_email = permission.user.email
    permission_collection_code = permission.collection.code
    res = res.click(_('Delete Permission')).follow()
    assert res.status_code == 200
    # Permission was deleted, so number of permissions are 1 less than initial state
    assert _('Successfully deleted permissions for "%(username)s" on collection "%(code)s".',
             username=permission_user_email, code=permission_collection_code) in res
    assert len(Permission.query.all()) == old_count - 1
