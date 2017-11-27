# -*- coding: utf-8 -*-
"""Test viewing user."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import escape, url_for
from flask_babel import gettext as _


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
