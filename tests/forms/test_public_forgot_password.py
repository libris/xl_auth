# -*- coding: utf-8 -*-
"""Test public ForgotPasswordForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import gettext as _

from xl_auth.public.forms import ForgotPasswordForm


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
