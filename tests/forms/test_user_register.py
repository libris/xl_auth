# -*- coding: utf-8 -*-
"""Test user RegisterForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
from flask_babel import gettext as _
from wtforms.validators import ValidationError

from xl_auth.user.forms import RegisterForm


def test_validate_success(superuser):
    """Register user with success."""
    form = RegisterForm(superuser, username='first.last@kb.se', full_name='First Last',
                        send_password_reset_email=False)

    assert form.validate() is True


def test_validate_without_full_name(superuser):
    """Attempt registering user with name shorter than 3 chars."""
    form = RegisterForm(superuser, username='librarian@kb.se', full_name='01')

    assert form.validate() is False
    assert _('Field must be between 3 and 255 characters long.') in form.full_name.errors


def test_validate_email_already_registered(superuser):
    """Attempt registering user with email that is already registered."""
    form = RegisterForm(superuser, username=superuser.email, full_name='Another Name')

    assert form.validate() is False
    assert _('Email already registered') in form.username.errors


def test_validate_email_already_registered_with_different_casing(superuser):
    """Attempt registering email that is already registered, this time with different casing."""
    superuser.email = 'SOMEONE@UPPERCASE-CLUB.se'
    superuser.save()
    form = RegisterForm(superuser, username=superuser.email.lower(), full_name='Too Similar')

    assert form.validate() is False
    assert _('Email already registered') in form.username.errors


def test_validate_regular_user(user):
    """Attempt to register user as regular user."""
    form = RegisterForm(user, username='first.last@kb.se', full_name='First Last')

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert e_info.value.args[0] == _('You do not have sufficient privileges for this operation.')
