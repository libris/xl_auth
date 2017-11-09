# -*- coding: utf-8 -*-
"""Test public LoginForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import gettext as _

from xl_auth.public.forms import LoginForm


def test_login_form_validate_success(user):
    """Login successful."""
    user.set_password('example')
    user.save()
    form = LoginForm(username=user.email, password='example')
    assert form.validate() is True
    assert form.user == user


def test_login_form_validate_success_with_different_username_casing(user):
    """Login successful, but this time with username/email in different casing."""
    user.email = 'me@lowercase-club.se'
    user.set_password('example')
    user.save()
    form = LoginForm(username=user.email.upper(), password='example')
    assert form.validate() is True
    assert form.user == user


# noinspection PyUnusedLocal
def test_login_form_validate_unknown_username(db):
    """Unknown username."""
    form = LoginForm(username='unknown@example.com', password='example')
    assert form.validate() is False
    assert _('Unknown username/email') in form.username.errors
    assert form.user is None


def test_login_form_validate_invalid_password(user):
    """Invalid password."""
    user.set_password('example')
    user.save()
    form = LoginForm(username=user.email, password='wrongPassword')
    assert form.validate() is False
    assert _('Invalid password') in form.password.errors


def test_login_form_validate_inactive_user(user):
    """Inactive user."""
    user.active = False
    user.set_password('example')
    user.save()
    # Correct username and password, but user is not activated.
    form = LoginForm(username=user.email, password='example')
    assert form.validate() is False
    assert _('User not activated') in form.username.errors
