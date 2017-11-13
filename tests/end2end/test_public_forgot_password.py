# -*- coding: utf-8 -*-
"""Test requesting a password reset."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta

from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.models import PasswordReset


def test_can_initiate_password_reset_flow(user, testapp):
    """Successfully requests a password reset using 'Forgot Password?' button."""
    # Goes to homepage.
    res = testapp.get('/')
    # Clicks on 'Forgot password'.
    res = res.click(_('Forgot password?'))
    # Fills out ForgotPasswordForm.
    username_with_different_casing = user.email.upper()  # Default would be userN@example.com.
    form = res.forms['forgotPasswordForm']
    form['username'] = username_with_different_casing
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200

    # New PasswordReset is added.
    password_reset = PasswordReset.query.filter_by(user=user).first()
    assert password_reset.is_active is True
    assert password_reset.expires_at > (datetime.utcnow() + timedelta(seconds=3600))


# noinspection PyUnusedLocal
def test_sees_error_message_if_username_does_not_exist(user, testapp):
    """Show error if username doesn't exist."""
    # Goes to 'Forgot Password?' page.
    res = testapp.get(url_for('public.forgot_password'))
    # Fills out ForgotPasswordForm.
    form = res.forms['forgotPasswordForm']
    form['username'] = 'unknown@example.com'
    # Submits.
    res = form.submit()
    # Sees error.
    assert _('Unknown username/email') in res

    # No PasswordReset is added.
    password_reset = PasswordReset.query.filter_by(user=user).first()
    assert password_reset is None
