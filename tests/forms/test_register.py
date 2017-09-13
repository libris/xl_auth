# -*- coding: utf-8 -*-
"""Test register form."""

from __future__ import absolute_import, division, print_function, unicode_literals

from xl_auth.user.forms import RegisterForm


# noinspection PyUnusedLocal
def test_validate_without_full_name(db):
    """Attempt registering with name shorter than 3 chars."""
    form = RegisterForm(email='mr.librarian@kb.se', full_name='01',
                        password='example', confirm='example')

    assert form.validate() is False
    assert 'Field must be between 3 and 255 characters long.' in form.full_name.errors


def test_validate_email_already_registered(user):
    """Enter email that is already registered."""
    form = RegisterForm(email=user.email, full_name='Another Name Perhaps',
                        password='example', confirm='example')

    assert form.validate() is False
    assert 'Email already registered' in form.email.errors


# noinspection PyUnusedLocal
def test_validate_success(db):
    """Register with success."""
    form = RegisterForm(email='first.last@kb.se', full_name='First Last',
                        password='example', confirm='example')
    assert form.validate() is True
