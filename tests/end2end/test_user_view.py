# -*- coding: utf-8 -*-
"""Test viewing user."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.models import User


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


def test_user_sees_error_message_if_when_user_id_does_not_exist(user, testapp):
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
