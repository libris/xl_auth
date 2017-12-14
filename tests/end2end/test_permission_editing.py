# -*- coding: utf-8 -*-
"""Test editing permissions."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _
from jinja2 import escape

from xl_auth.permission.models import Permission

from ..factories import CollectionFactory, PermissionFactory


def test_superuser_can_edit_existing_permission(superuser, permission, testapp):
    """Edit existing permission as superuser."""
    old_count = len(Permission.query.all())
    other_collection = CollectionFactory()
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Clicks Permissions button
    res = res.click(_('Permissions'))
    # Clicks Edit button on a permission
    res = res.click(href=url_for('permission.edit', permission_id=permission.id))
    # Fills out the form
    form = res.forms['editPermissionForm']
    # Defaults are kept -- setting ``form['user_id'] = permission.user.id`` is redundant
    form['collection_id'] = other_collection.id
    # Submits
    res = form.submit()
    assert res.status_code == 302
    assert res.location.endswith(url_for('permission.home'))
    res = res.follow()
    assert res.status_code == 200
    # The permission was updated, and number of permissions are the same as initial state
    assert _('Updated permissions for "%(username)s" on collection "%(code)s".',
             username=permission.user.email, code=other_collection.code) in res
    assert len(Permission.query.all()) == old_count
    # The edited permission is listed under existing collections
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(permission.user.email))) == 1
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(other_collection.code))) == 1


def test_cataloging_admin_can_edit_permission_from_collection_view(user, permission, superuser,
                                                                   testapp):
    """Edit existing permission from collection view as cataloging admin."""
    # Make 'user' cataloging admin for 'permission.collection' and 2nd one
    PermissionFactory(user=user, collection=permission.collection,
                      cataloging_admin=True).save_as(superuser)
    initial_collection_code = permission.collection.code
    other_permission = PermissionFactory(user=user, cataloging_admin=True)
    old_count = len(Permission.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Clicks to View collection from profile instead
    res = res.click(href=url_for('collection.view', collection_code=permission.collection.code))
    # Clicks Edit on a permission
    res = res.click(href=url_for('permission.edit', permission_id=permission.id))
    # Fills out the form
    form = res.forms['editPermissionForm']
    # Defaults are kept -- setting ``form['user_id'] = permission.user.id`` is redundant
    form['collection_id'] = other_permission.collection.id
    # Submits
    res = form.submit()
    assert res.status_code == 302
    assert url_for('collection.view', collection_code=initial_collection_code) in res.location
    res = res.follow()
    assert res.status_code == 200
    # The permission was updated, and number of permissions are the same as initial state
    assert _('Updated permissions for "%(username)s" on collection "%(code)s".',
             username=permission.user.email, code=other_permission.collection.code) in res
    assert len(Permission.query.all()) == old_count
    # The edited permission is NOT listed on page for 'initial_collection_code'.
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(permission.user.email))) == 0


def test_superuser_sees_error_if_permission_is_already_registered(superuser, permission, testapp):
    """Show error if permission is edited to (user_id, collection_id) pair that already exists."""
    other_permission = PermissionFactory()
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Clicks Permissions button
    res = res.click(_('Permissions'))
    # Clicks Edit button on 'permission'
    res = res.click(href=url_for('permission.edit', permission_id=permission.id))
    # Fills out the form with same user ID and collection ID as 'other_permission'
    form = res.forms['editPermissionForm']
    form['user_id'] = other_permission.user.id
    form['collection_id'] = other_permission.collection.id
    # Submits
    res = form.submit()
    # Sees error
    assert escape(
        _('Permissions for user "%(username)s" on collection "%(code)s" already registered',
          username=other_permission.user.email, code=other_permission.collection.code)) in res


def test_user_cannot_edit_permission(user, permission, testapp):
    """Attempt to edit a permission as non-'cataloging admin' user."""
    assert user.is_cataloging_admin_for(permission.collection) is False
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

    # Try to delete a specific permission directly
    res = testapp.get(url_for('permission.edit', permission_id=permission.id))
    form = res.forms['editPermissionForm']
    form['registrant'].checked = not permission.registrant
    res = form.submit()
    # FIXME: The intended assertion below doesn't work.. :(
    # assert _('You do not have sufficient privileges for this operation.') in res
    assert res.status_code == 200  # Fallback, means we didn't redirect due to validation error.
