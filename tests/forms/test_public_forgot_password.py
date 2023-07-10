"""Test public ForgotPasswordForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta

from flask_babel import gettext as _

from xl_auth.public.forms import ForgotPasswordForm

from ..factories import PasswordResetFactory


# noinspection PyUnusedLocal
def test_validate_unknown_username(db):
    """Unknown username."""
    form = ForgotPasswordForm(username='unknown@example.com')

    assert form.validate() is False
    assert _('Unknown username/email') in form.username.errors


def test_validate_success(user):
    """Validate using the expected field."""
    form = ForgotPasswordForm(username=user.email)

    assert form.validate() is True


def test_validate_too_many_recent_active_resets(app, user):
    """Too many recent active resets."""
    old_active_reset = PasswordResetFactory(user=user)
    old_active_reset.created_at = datetime.utcnow() - timedelta(hours=3)
    PasswordResetFactory(user=user)

    form = ForgotPasswordForm(username=user.email)

    # One active but old and one active and recent are fine
    assert form.validate() is True

    PasswordResetFactory(user=user)

    form = ForgotPasswordForm(username=user.email)

    # Two active and recent are not fine
    assert form.validate() is False
    assert _('You already have an active password reset. Please check your email inbox (and your '
             'Spam folder) or try again later.') in form.username.errors
