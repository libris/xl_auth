# -*- coding: utf-8 -*-
"""Test viewing user."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import escape, url_for
from flask_babel import gettext as _

from xl_auth.collection.models import Collection

from ..factories import PermissionFactory


def test_user_can_view_collection_info(permission, testapp):
    """View info about one of the user's collections."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = permission.user.email
    form['password'] = 'example'
    # Submits.
    res = form.submit().follow()
    # Clicks 'view collection' on profile page
    res = res.click(href=url_for('collection.view', collection_code=permission.collection.code))
    # Sees collection info.
    assert res.status_code is 200
    assert _('View Collection \'%(code)s\'', code=permission.collection.code) in res


def test_user_sees_error_message_if_collection_code_does_not_exist(user, testapp):
    """Show error when attempting to view a permission that does not exist."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code is 200
    # Fails to figures out the correct ID for another user.
    res = testapp.get(url_for('collection.view', collection_code='FAKE1')).follow()
    # Sees error message.
    assert escape(_('Collection code "%(code)s" does not exist', code='FAKE1')) in res


def test_superuser_can_view_all_permissions_on_collection(superuser, permission, testapp):
    """View all permissions as superuser."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code is 200
    # Goes to the right URL for viewing a collection.
    res = testapp.get(url_for('collection.view', collection_code=permission.collection.code))
    assert res.status_code is 200
    # Sees all permissions.
    assert _('Permissions') in res
    assert permission.user.email in res


def test_cataloging_admin_can_view_all_permissions_on_own_collection(user, collection, testapp):
    """View all permissions on a collection that you're managing."""
    # Add cataloging admin permission.
    cataloging_admin_permission = PermissionFactory(user=user, collection=collection,
                                                    cataloging_admin=True)
    cataloging_admin_permission.save()
    # Add 2nd cataloger+registrant permission.
    other_users_non_cataloging_admin_permission = PermissionFactory(collection=collection,
                                                                    cataloging_admin=False)
    other_users_non_cataloging_admin_permission.save()
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code is 200
    # Goes to the right URL for viewing a collection.
    res = testapp.get(url_for('collection.view',
                              collection_code=cataloging_admin_permission.collection.code))
    assert res.status_code is 200
    # Sees all permissions.
    assert _('Permissions') in res
    assert cataloging_admin_permission.user.email in res
    assert other_users_non_cataloging_admin_permission.user.email in res
