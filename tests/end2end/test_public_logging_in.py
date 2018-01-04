# -*- coding: utf-8 -*-
"""Test logging in."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

from flask import current_app, url_for
from flask_babel import gettext as _

from xl_auth.user.models import FailedLoginAttempt, User


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


def test_user_must_approve_tos_on_login_if_unset(user, testapp):
    """After login, the user is requested to approve ToS if not done already."""
    user.tos_approved_at = None
    user.save()
    # Goes to pages that requires authentication and gets redirected to login page.
    res = testapp.get('/collections/?foo=1&baz=2').follow()
    # Fills out login form.
    username_with_different_casing = user.email.upper()
    form = res.forms['loginForm']
    form['username'] = username_with_different_casing
    form['password'] = 'myPrecious'
    # Submits and gets redirected to approve ToS view.
    res = form.submit()
    assert res.status_code == 302
    assert '/users/approve_tos' in res.location
    res = res.follow()
    assert res.status_code == 200
    assert _('Approve ToS') in res
    form = res.forms['approveForm']
    form['tos_approved'] = 'y'
    res = form.submit()
    # Gets redirected to path initially requested.
    assert res.status_code == 302
    assert '/collections/?foo=1&baz=2' in res.location
    res = res.follow()
    assert res.status_code == 200
    assert _('Collections') in res
    # Logout and login again.
    res = res.click(href='/logout/').follow()
    assert res.status_code == 200
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits and gets redirected to profile view instead of approve ToS (as it's already done).
    res = form.submit()
    assert res.status_code == 302
    assert '/users/approve_tos' not in res.location
    assert res.location.endswith('/users/profile/')


def test_unauthorized_leads_to_login_which_follows_next_redirect_param_on_success(user, testapp):
    """Redirect using 'next' query param if set."""
    # Goes to pages that requires authentication.
    res = testapp.get('/oauth/authorize?param1=value1&param2=value2').follow()
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email,
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit()
    assert res.status_code == 302
    assert '/oauth/authorize?param1=value1&param2=value2' in res.location


def test_successful_login_updates_last_login_at_only(user, testapp):
    """Successful login sets 'last_login_at' to current UTC datetime (but not 'modified_*')."""
    # Check expected premises.
    assert user.last_login_at is None
    initial_modified_at = user.modified_at
    initial_modified_by = user.modified_by
    assert initial_modified_by != user
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200

    # Fetch user from database, now with login timestamp but no modified at/by changes.
    updated_user = User.get_by_id(user.id)
    assert isinstance(updated_user.last_login_at, datetime)
    assert (datetime.utcnow() - updated_user.last_login_at).total_seconds() < 10
    assert updated_user.modified_at == initial_modified_at
    assert updated_user.modified_by == initial_modified_by


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
    # Fills out login form, username incorrect.
    form = res.forms['loginForm']
    form['username'] = 'unknown@nowhere.com'
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit()
    # Sees error.
    assert _('Unknown username/email') in res


def test_block_login_on_too_many_failed_attempts(user, testapp):
    """Temporarily block login if too many failed attempts."""
    current_app.config['XL_AUTH_FAILED_LOGIN_MAX_ATTEMPTS'] = 1
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

    # Goes to homepage a second time.
    res = testapp.get('/')
    # Fills out login form, password incorrect.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'wrong'
    # Submits and sees error.
    res = form.submit(expect_errors=True)
    assert res.status_code == 429

    FailedLoginAttempt.purge_failed_for_username_and_ip(user.email, '127.0.0.1')

    # Goes to homepage a third time.
    res = testapp.get('/')
    # Fills out login form, password incorrect.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200
