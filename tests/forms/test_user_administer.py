# -*- coding: utf-8 -*-
"""Test user AdministerForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice

import pytest
from flask_babel import gettext as _
from wtforms.validators import ValidationError

from xl_auth.user.forms import AdministerForm


def test_validate_success(superuser):
    """Edit user details with success."""
    form = AdministerForm(superuser, superuser.email, username=superuser.email,
                          full_name='My New Name',
                          is_active=not superuser.is_active, is_admin=not superuser.is_admin)

    assert form.validate() is True


# noinspection PyUnusedLocal
def test_validate_username_does_not_exist(db, superuser):
    """Attempt to edit user details with a username that is not registered."""
    form = AdministerForm(superuser, 'missing@example.com', username='missing@example.com',
                          full_name='FooBar', is_active=choice([True, False]),
                          is_admin=choice([True, False]))

    assert form.validate() is False
    assert _('User does not exist') in form.username.errors


def test_validate_modifying_username(superuser):
    """Attempt to edit user by giving it a new username/email."""
    form = AdministerForm(superuser, superuser.email, username='new.address@kb.se',
                          full_name=superuser.full_name,
                          is_active=superuser.is_active, is_admin=superuser.is_admin)

    assert form.validate() is False
    assert _('Email cannot be modified') in form.username.errors


def test_as_regular_user(user):
    """Attempt to use administer form as regular user."""
    form = AdministerForm(user, user.email, username=user.email,
                          full_name=user.full_name,
                          is_active=user.is_active, is_admin=True)

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert e_info.value.args[0] == _('You do not have sufficient privileges for this operation.')
