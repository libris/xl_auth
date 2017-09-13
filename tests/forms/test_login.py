# -*- coding: utf-8 -*-
"""Test login form."""

from __future__ import absolute_import, division, print_function, unicode_literals

from xl_auth.public.forms import LoginForm


def test_validate_success(user):
    """Login successful."""
    user.set_password('example')
    user.save()
    form = LoginForm(username=user.email, password='example')
    assert form.validate() is True
    assert form.user == user


# noinspection PyUnusedLocal
def test_validate_unknown_username(db):
    """Unknown username."""
    form = LoginForm(username='unknown@example.com', password='example')
    assert form.validate() is False
    assert 'Unknown username/email' in form.username.errors
    assert form.user is None


def test_validate_invalid_password(user):
    """Invalid password."""
    user.set_password('example')
    user.save()
    form = LoginForm(username=user.email, password='wrongPassword')
    assert form.validate() is False
    assert 'Invalid password' in form.password.errors


def test_validate_inactive_user(user):
    """Inactive user."""
    user.active = False
    user.set_password('example')
    user.save()
    # Correct username and password, but user is not activated.
    form = LoginForm(username=user.email, password='example')
    assert form.validate() is False
    assert 'User not activated' in form.username.errors
