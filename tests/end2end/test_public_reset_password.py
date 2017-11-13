# -*- coding: utf-8 -*-
"""Test resetting password."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta

from flask import url_for
from flask_babel import gettext as _
from jinja2 import escape
from xl_auth.user.models import PasswordReset


def test_can_complete_password_reset_flow(password_reset, testapp):
    """Successfully reset password."""
    # Goes to reset password link.
    res = testapp.get(url_for('public.reset_password', email=password_reset.user.email,
                              code=password_reset.code))
    # Fills out ResetPasswordForm.
    form = res.forms['resetPasswordForm']
    form['confirm'] = form['password'] = 'unicorns are real'
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200

    # PasswordReset no longer active and password update succeeded.
    updated_password_reset = PasswordReset.query.filter_by(user=password_reset.user).first()
    assert updated_password_reset.is_active is False
    assert updated_password_reset.user.check_password('unicorns are real') is True


# noinspection PyUnusedLocal
def test_sees_error_message_if_username_does_not_match_exist(user, password_reset, testapp):
    """Show error if username doesn't match code."""
    assert user != password_reset.user

    # Goes to reset password link.
    res = testapp.get(url_for('public.reset_password', email=user.email,
                              code=password_reset.code))
    # Fills out ResetPasswordForm.
    form = res.forms['resetPasswordForm']
    form['confirm'] = form['password'] = 'superSecret'
    # Submits.
    res = form.submit()
    # Sees error.
    assert escape(_('Reset code "%(code)s" does not exit', code=password_reset.code)) in res


# noinspection PyUnusedLocal
def test_sees_error_message_if_reset_code_is_expired(password_reset, testapp):
    """Show error if reset code has expired."""
    password_reset.expires_at = datetime.utcnow() - timedelta(seconds=1)
    password_reset.save()
    # Goes to reset password link.
    res = testapp.get(url_for('public.reset_password', email=password_reset.user.email,
                              code=password_reset.code))
    # Fills out ResetPasswordForm.
    form = res.forms['resetPasswordForm']
    form['confirm'] = form['password'] = 'superSecret'
    # Submits.
    res = form.submit()
    # Sees error.
    assert escape(_('Reset code "%(code)s" expired at %(isoformat)s', code=password_reset.code,
                    isoformat=password_reset.expires_at.isoformat() + 'Z')) in res


# noinspection PyUnusedLocal
def test_sees_error_message_if_attempting_to_use_reset_code_twice(password_reset, testapp):
    """Show error if reset code has aleady been used."""
    # Goes to reset password link.
    res = testapp.get(url_for('public.reset_password', email=password_reset.user.email,
                              code=password_reset.code))
    # Fills out ResetPasswordForm.
    form = res.forms['resetPasswordForm']
    form['confirm'] = form['password'] = 'superSecret'
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200

    # Does the same thing again.
    res = testapp.get(url_for('public.reset_password', email=password_reset.user.email,
                              code=password_reset.code))
    form = res.forms['resetPasswordForm']
    form['confirm'] = form['password'] = 'superSecret'
    res = form.submit()
    # Sees error.
    assert escape(_('Reset code "%(code)s" already used (%(isoformat)s)', code=password_reset.code,
                    isoformat=password_reset.modified_at.isoformat() + 'Z')) in res
