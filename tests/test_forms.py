# -*- coding: utf-8 -*-
"""Test forms."""

from xl_auth.public.forms import LoginForm


class TestLoginForm(object):
    """Login form."""

    def test_validate_success(self, user):
        """Login successful."""

        user.set_password('example')
        user.save()
        form = LoginForm(username=user.username, password='example')
        assert form.validate() is True
        assert form.user == user

    # noinspection PyUnusedLocal
    def test_validate_unknown_username(self, db):
        """Unknown username."""

        form = LoginForm(username='unknown', password='example')
        assert form.validate() is False
        assert 'Unknown username' in form.username.errors
        assert form.user is None

    def test_validate_invalid_password(self, user):
        """Invalid password."""

        user.set_password('example')
        user.save()
        form = LoginForm(username=user.username, password='wrongPassword')
        assert form.validate() is False
        assert 'Invalid password' in form.password.errors

    def test_validate_inactive_user(self, user):
        """Inactive user."""

        user.active = False
        user.set_password('example')
        user.save()
        # Correct username and password, but user is not activated.
        form = LoginForm(username=user.username, password='example')
        assert form.validate() is False
        assert 'User not activated' in form.username.errors
