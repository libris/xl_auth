# -*- coding: utf-8 -*-
"""Test registering permissions."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import gettext as _
from jinja2 import escape

from xl_auth.permission.models import Permission


# noinspection PyUnusedLocal
def test_user_can_register_new_permission(user, collection, testapp):
    """Register a new permission."""
    old_count = len(Permission.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form in navbar
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Clicks Permissions button
    res = res.click(_('Permissions'))
    # Clicks Register New Permission button
    res = res.click(_('New Permission'))
    # Fills out the form
    form = res.forms['registerPermissionForm']
    form['user_id'] = user.id
    form['collection_id'] = collection.id
    # Submits
    res = form.submit().follow()
    assert res.status_code == 200
    # A new permission was created
    assert _('Added permissions for "%(username)s" on collection "%(code)s".',
             username=user.email, code=collection.code) in res
    assert len(Permission.query.all()) == old_count + 1
    # The new permission is listed under existing collections
    assert '<td>{}</td>'.format(user.email) in res
    assert '<td>{}</td>'.format(collection.code) in res


# noinspection PyUnusedLocal
def test_user_sees_error_message_if_permission_is_already_registered(user, permission, testapp):
    """Show error if permission is already registered."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form in navbar
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Clicks Permissions button
    res = res.click(_('Permissions'))
    # Clicks Register New Permission button
    res = res.click(_('New Permission'))
    # Fills out the form with same user ID and collection ID as (existing) 'permission'
    form = res.forms['registerPermissionForm']
    form['user_id'] = permission.user.id
    form['collection_id'] = permission.collection.id
    # Submits
    res = form.submit()
    # Sees error
    assert escape(
        _('Permissions for user "%(username)s" on collection "%(code)s" already registered',
          username=permission.user.email, code=permission.collection.code)) in res
