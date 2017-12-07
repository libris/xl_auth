# -*- coding: utf-8 -*-
"""Test viewing user."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.models import User

from ..factories import PermissionFactory


def test_user_can_view_others_user(user, superuser, testapp):
    """View user info as another user."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code is 200
    # Cleverly figures out the right URL for another user.
    res = testapp.get(url_for('user.view', user_id=superuser.id))
    # Sees user info.
    assert res.status_code is 200
    assert _('View User \'%(email)s\'', email=superuser.email) in res


def test_user_sees_error_message_if_user_id_does_not_exist(user, testapp):
    """Show error when attempting to view a user that does not exist."""
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
    last_user = User.query.all()[-1]
    made_up_id = last_user.id + 1
    res = testapp.get(url_for('user.view', user_id=made_up_id)).follow()
    # Sees error message.
    assert _('User ID "%(user_id)s" does not exist', user_id=made_up_id) in res


def test_superuser_can_view_all_permissions_on_other_user(superuser, user, testapp):
    """View all permissions as superuser."""
    # Add cataloging admin permission.
    cataloging_admin_permission = PermissionFactory(user=user, cataloging_admin=True)
    cataloging_admin_permission.save()
    # Add 2nd cataloger+registrant permission.
    non_cataloging_admin_permission = PermissionFactory(user=user, cataloging_admin=False)
    non_cataloging_admin_permission.save()
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code is 200
    # Cleverly figures out the right URL for their profile page.
    res = testapp.get(url_for('user.view', user_id=user.id))
    assert res.status_code is 200
    # Sees all permissions.
    assert _('Permissions') in res
    assert cataloging_admin_permission.collection.code in res
    assert non_cataloging_admin_permission.collection.code in res


def test_user_can_view_all_permissions_on_thyself(user, testapp):
    """View all your permissions as thyself."""
    # Add cataloging admin permission.
    cataloging_admin_permission = PermissionFactory(user=user, cataloging_admin=True)
    cataloging_admin_permission.save()
    # Add 2nd cataloger+registrant permission.
    non_cataloging_admin_permission = PermissionFactory(user=user, cataloging_admin=False)
    non_cataloging_admin_permission.save()
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code is 200
    # Cleverly figures out the right URL for their profile page.
    res = testapp.get(url_for('user.view', user_id=user.id))
    assert res.status_code is 200
    # Sees all permissions.
    assert _('Permissions') in res
    assert cataloging_admin_permission.collection.code in res
    assert non_cataloging_admin_permission.collection.code in res


def test_user_can_only_view_cataloging_admin_permissions_on_others_when_not_admin(user, testapp):
    """View only 'cataloging_admin' permissions on others except for collections you administer."""
    # Add user with cataloging admin permission.
    other_users_cataloging_admin_permission = PermissionFactory(cataloging_admin=True)
    other_users_cataloging_admin_permission.save()
    # Add another user with cataloger+registrant permission.
    another_users_non_cataloging_admin_permission = PermissionFactory(cataloging_admin=False)
    another_users_non_cataloging_admin_permission.save()
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code is 200
    # Checks out another user that has a cataloging admin privilege.
    res = testapp.get(
        url_for('user.view', user_id=other_users_cataloging_admin_permission.user.id))
    assert res.status_code is 200
    # Sees the cataloging admin permission.
    assert other_users_cataloging_admin_permission.collection.code in res
    # Checks out another user that DOES NOT have cataloging admin rights only cataloger/registrant.
    res = testapp.get(
        url_for('user.view', user_id=another_users_non_cataloging_admin_permission.user.id))
    assert res.status_code is 200
    # Does NOT see the non-admin level permission.
    collection_view_url = url_for('collection.view',
                                  collection_code=another_users_non_cataloging_admin_permission
                                  .collection.code)
    assert collection_view_url not in res
    # Except where the viewer a cataloging admin for the target collection...
    cataloging_admin_permission_for_viewer = PermissionFactory(
        user=user,
        collection=another_users_non_cataloging_admin_permission.collection,
        cataloging_admin=True
    )
    cataloging_admin_permission_for_viewer.save()
    res = testapp.get(
        url_for('user.view', user_id=another_users_non_cataloging_admin_permission.user.id))
    assert res.status_code is 200
    assert _('You will only see all permissions for those collections that you are cataloging '
             'administrator for.') in res
    assert collection_view_url in res
