# -*- coding: utf-8 -*-
"""Test logging in."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.models import User


def test_can_log_in_returns_200(user, testapp):
    """Login successful (irrespective of casing)."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    username_with_different_casing = user.email.upper()  # Default would be userN@example.com.
    form = res.forms['loginForm']
    form['username'] = username_with_different_casing
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200


def test_unauthorized_leads_to_login_which_follows_next_param_on_success(user, testapp):
    """Redirect using 'next' query param if set."""
    # Goes to pages that requires authentication.
    res = testapp.get('/oauth/authorize?param1=value1&param2=value2').follow()
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email,
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit()
    assert '/oauth/authorize?param1=value1&param2=value2' in res.location


def test_successful_login_updates_last_login_at(user, testapp):
    """Successful login sets 'last_login_at' to current UTC datetime."""
    assert user.last_login_at is None

    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200

    # Fetch user from database, now with login timestamp.
    updated_user = User.get_by_id(user.id)
    assert isinstance(updated_user.last_login_at, datetime)
    assert (datetime.utcnow() - updated_user.last_login_at).total_seconds() < 10


def test_sees_alert_on_log_out(user, testapp):
    """Show alert on logout."""
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    form.submit().follow()
    res = testapp.get(url_for('public.logout')).follow()
    # Sees alert.
    assert _('You are logged out.') in res


def test_sees_error_message_if_password_is_incorrect(user, testapp):
    """Show error if password is incorrect."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form, password incorrect.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'wrong'
    # Submits.
    res = form.submit()
    # Sees error.
    assert _('Invalid password') in res


# noinspection PyUnusedLocal
def test_sees_error_message_if_username_doesnt_exist(user, testapp):
    """Show error if username doesn't exist."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form, password incorrect.
    form = res.forms['loginForm']
    form['username'] = 'unknown@nowhere.com'
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit()
    # Sees error.
    assert _('Unknown username/email') in res
