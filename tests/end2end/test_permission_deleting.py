# -*- coding: utf-8 -*-
"""Test deleting permissions."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _

from xl_auth.permission.models import Permission

from ..factories import PermissionFactory


def test_superuser_can_delete_existing_permission(superuser, permission, testapp):
    """Delete existing permission as superuser."""
    old_count = len(Permission.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    assert res.status_code == 200
    # Goes to Permissions' overview
    res = testapp.get(url_for('permission.home'))
    # Clicks Delete button on a permission
    permission_user_email = permission.user.email
    permission_collection_code = permission.collection.code
    res = res.click(href=url_for('permission.delete', permission_id=permission.id) +
                    '\?next=' + url_for('permission.home'))
    assert res.status_code == 200
    assert _('Acknowledge Deletion') in res
    assert _('Delete permission for "%(username)s" on collection "%(code)s"?',
             username=permission_user_email, code=permission_collection_code) in res
    form = res.forms['deletePermissionForm']
    form['acknowledged'] = 'y'
    res = form.submit()
    assert res.status_code == 302
    assert url_for('permission.home') in res.location
    res = res.follow()
    # Permission was deleted, so number of permissions are 1 less than initial state
    assert _('Successfully deleted permissions for "%(username)s" on collection "%(code)s".',
             username=permission_user_email, code=permission_collection_code) in res
    assert len(Permission.query.all()) == old_count - 1


def test_cataloging_admin_can_delete_existing_permission(user, permission, superuser, testapp):
    """Delete existing permission as cataloging admin for a collection."""
    PermissionFactory(user=user, collection=permission.collection,
                      cataloging_admin=True).save_as(superuser)
    assert user.is_cataloging_admin_for(permission.collection) is True
    old_count = len(Permission.query.all())
    permission_user_email = permission.user.email
    permission_collection_code = permission.collection.code
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # We see no Permissions button
    assert res.lxml.xpath("//a[contains(@text,'{0}')]".format(_('Permissions'))) == []

    # Try to go there directly and fail
    testapp.get('/permissions/', status=403)

    # Go to profile instead and click through delete flow
    res = testapp.get(url_for('user.profile'))
    res = res.click(href=url_for('collection.view', collection_code=permission_collection_code))
    res = res.click(href=url_for('permission.delete', permission_id=permission.id))
    form = res.forms['deletePermissionForm']
    form['acknowledged'] = 'y'
    res = form.submit()
    assert res.status_code == 302
    assert url_for('collection.view', collection_code=permission_collection_code) in res.location
    res = res.follow()

    # Permission was deleted, so number of permissions are 1 less than initial state
    assert _('Successfully deleted permissions for "%(username)s" on collection "%(code)s".',
             username=permission_user_email, code=permission_collection_code) in res
    assert len(Permission.query.all()) == old_count - 1


def test_user_cannot_delete_permission(user, permission, superuser, testapp):
    """Attempt to delete a permission as non-'cataloging admin' user."""
    assert user.is_cataloging_admin_for(permission.collection) is False
    assert user.is_cataloging_admin is False
    old_count = len(Permission.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # We see no Permissions button
    assert res.lxml.xpath("//a[contains(@text,'{0}')]".format(_('Permissions'))) == []

    # Try to go there directly
    testapp.get('/permissions/', status=403)

    # Try to delete a specific permission with direct URL
    testapp.get(url_for('permission.delete', permission_id=permission.id), status=403)

    # Accidentally be cataloging admin for unrelated collection and try again
    temp_permission = PermissionFactory(user=user, cataloging_admin=True).save_as(superuser)
    res = testapp.get(url_for('permission.delete', permission_id=permission.id))
    form = res.forms['deletePermissionForm']
    form['acknowledged'] = 'y'
    res = form.submit()
    assert _('You do not have sufficient privileges for this operation.') in res
    temp_permission.delete()

    # Nothing was deleted
    assert len(Permission.query.all()) == old_count
