# -*- coding: utf-8 -*-
"""Test user form(s)."""

from __future__ import absolute_import, division, print_function, unicode_literals

from xl_auth.user.forms import RegisterForm


# noinspection PyUnusedLocal
def test_register_form_validate_without_full_name(db):
    """Attempt registering with name shorter than 3 chars."""
    form = RegisterForm(username='mr.librarian@kb.se', full_name='01',
                        password='example', confirm='example')

    assert form.validate() is False
    assert 'Field must be between 3 and 255 characters long.' in form.full_name.errors


def test_register_form_validate_email_already_registered(user):
    """Enter email that is already registered."""
    form = RegisterForm(username=user.email, full_name='Another Name Perhaps',
                        password='example', confirm='example')

    assert form.validate() is False
    assert 'Email already registered' in form.username.errors


# noinspection PyUnusedLocal
def test_register_form_validate_success(db):
    """Register with success."""
    form = RegisterForm(username='first.last@kb.se', full_name='First Last',
                        password='example', confirm='example')
    assert form.validate() is True
