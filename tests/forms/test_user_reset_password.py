# -*- coding: utf-8 -*-
"""Test user ResetPasswordForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta

from flask_babel import gettext as _

from xl_auth.user.forms import ResetPasswordForm


def test_validate_with_incorrect_code(password_reset, user):
    """Attempt resetting password with another user's reset code."""
    other_user = user  # For clarity.
    form = ResetPasswordForm(code=password_reset.code, username=other_user.email,
                             password='123456', confirm='123456')

    assert form.validate() is False
    assert _('Reset code "%(code)s" does not exit', code=password_reset.code) in form.code.errors


def test_validate_with_expired_code(password_reset):
    """Attempt resetting password with an expired reset code."""
    password_reset.expires_at = datetime.utcnow() - timedelta(seconds=1)
    password_reset.save()
    form = ResetPasswordForm(code=password_reset.code, username=password_reset.user.email,
                             password='123456', confirm='123456')

    assert form.validate() is False
    assert _('Reset code "%(code)s" expired at "%(isoformat)s"', code=password_reset.code,
             isoformat=password_reset.expires_at.isoformat() + 'Z') in form.code.errors


def test_validate_with_inactive_code(password_reset):
    """Attempt resetting password with an inactive reset code."""
    password_reset.is_active = False
    password_reset.save()
    form = ResetPasswordForm(code=password_reset.code, username=password_reset.user.email,
                             password='123456', confirm='123456')

    assert form.validate() is False
    assert _('Reset code "%(code)s" already used ("%(isoformat)s")', code=password_reset.code,
             isoformat=password_reset.modified_at.isoformat() + 'Z') == form.code.errors[0]


def test_validate_success(password_reset):
    """Validate using all the expected fields."""
    form = ResetPasswordForm(code=password_reset.code, username=password_reset.user.email,
                             password='123456', confirm='123456')

    assert form.validate() is True
