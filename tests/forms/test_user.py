# -*- coding: utf-8 -*-
"""Test user forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice

import pytest
from flask_babel import gettext as _
from wtforms.validators import ValidationError

from xl_auth.user.forms import AdministerForm, ChangePasswordForm, EditDetailsForm, RegisterForm


# Registration form
#
# noinspection PyUnusedLocal
def test_register_form_validate_success(db, superuser):
    """Register user with success."""
    form = RegisterForm(superuser, username='first.last@kb.se', full_name='First Last',
                        password='example', confirm='example')

    assert form.validate() is True


# noinspection PyUnusedLocal
def test_register_form_validate_without_full_name(superuser, db):
    """Attempt registering user with name shorter than 3 chars."""
    form = RegisterForm(superuser, username='mr.librarian@kb.se', full_name='01',
                        password='example', confirm='example')

    assert form.validate() is False
    assert _('Field must be between 3 and 255 characters long.') in form.full_name.errors


def test_register_form_validate_email_already_registered(superuser):
    """Attempt registering user with email that is already registered."""
    form = RegisterForm(superuser, username=superuser.email, full_name='Another Name',
                        password='example', confirm='example')

    assert form.validate() is False
    assert _('Email already registered') in form.username.errors


def test_register_form_validate_email_already_registered_with_different_casing(superuser):
    """Attempt registering email that is already registered, this time with different casing."""
    superuser.email = 'SOMEONE@UPPERCASE-CLUB.se'
    superuser.save()
    form = RegisterForm(superuser, username=superuser.email.lower(), full_name='Too Similar',
                        password='example', confirm='example')

    assert form.validate() is False
    assert _('Email already registered') in form.username.errors


def test_register_form_validate_regular_user(db, user):
    """Attempt to register user as regular user."""
    form = RegisterForm(user, username='first.last@kb.se', full_name='First Last',
                        password='example', confirm='example')

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert str(e_info.value) == _('You do not have sufficient privileges for this operation.')


# Administration form
#
def test_admin_form_validate_success(superuser):
    """Edit user details with success."""
    form = AdministerForm(superuser, superuser.email, username=superuser.email,
                          full_name='My New Name',
                          active=not superuser.active, is_admin=not superuser.is_admin)

    assert form.validate() is True


# noinspection PyUnusedLocal
def test_admin_form_validate_username_does_not_exist(db, superuser):
    """Attempt to edit user details with a username that is not registered."""
    form = AdministerForm(superuser, 'missing@nowhere.com', username='missing@nowhere.com',
                          full_name='Mr Foo', active=choice([True, False]),
                          is_admin=choice([True, False]))

    assert form.validate() is False
    assert _('User does not exist') in form.username.errors


def test_admin_form_validate_modifying_username(superuser):
    """Attempt to edit user by giving it a new username/email."""
    form = AdministerForm(superuser, superuser.email, username='new.address@kb.se',
                          full_name=superuser.full_name,
                          active=superuser.active, is_admin=superuser.is_admin)

    assert form.validate() is False
    assert _('Email cannot be modified') in form.username.errors


def test_admin_form_as_regular_user(user):
    """Attempt to use administer form as regular user."""
    form = AdministerForm(user, user.email, username=user.email,
                          full_name=user.full_name,
                          active=user.active, is_admin=True)

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert str(e_info.value) == _('You do not have sufficient privileges for this operation.')


# Edit details form
#
def test_user_can_edit_self(user):
    """Edit own full_name with success."""
    form = EditDetailsForm(user, user.email, username=user.email, full_name='New Name')

    assert form.validate() is True


def test_user_cannot_edit_username(user):
    """Attempt to edit username."""
    form = EditDetailsForm(user, user.email, username='other@example.com', full_name=user.full_name)

    assert form.validate() is False
    assert _('Email cannot be modified') in form.username.errors


def test_user_cannot_edit_other(superuser, user):
    """Attempt to edit another user's details."""
    form = EditDetailsForm(user, superuser.email, username=superuser.email, full_name='New Name')

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert str(e_info.value) == _('You do not have sufficient privileges for this operation.')


# Change password form
#
def test_change_password_form_validate_modifying_username(superuser):
    """Attempt to change password but passing in a new username/email."""
    form = ChangePasswordForm(superuser, superuser.email, username='new.address@kb.se',
                              password='123456', confirm='123456')

    assert form.validate() is False
    assert _('Email cannot be modified') in form.username.errors


def test_change_password_form_validate_success(superuser):
    """Change user password with success."""
    form = ChangePasswordForm(superuser, superuser.email, username=superuser.email,
                              password='example', confirm='example')

    assert form.validate() is True


def test_change_password_form_as_user_validate_success(user):
    """Change user password with success."""
    form = ChangePasswordForm(user, user.email, username=user.email,
                              password='example', confirm='example')

    assert form.validate() is True


def test_user_change_password_form_for_other_user(superuser, user):
    """Change password for another user as admin."""
    form = ChangePasswordForm(user, superuser.email, username=superuser.email,
                              password='example', confirm='example')

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert str(e_info.value) == _('You do not have sufficient privileges for this operation.')


def test_superuser_change_password_form_for_other_user(superuser, user):
    """Attempt to change password for another user."""
    form = ChangePasswordForm(superuser, user.email, username=user.email,
                              password='example', confirm='example')

    assert form.validate() is True
