# -*- coding: utf-8 -*-
"""Test user forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice

from flask_babel import gettext as _

from xl_auth.user.forms import ChangePasswordForm, EditDetailsForm, RegisterForm


# noinspection PyUnusedLocal
def test_register_form_validate_without_full_name(db):
    """Attempt registering user with name shorter than 3 chars."""
    form = RegisterForm(username='mr.librarian@kb.se', full_name='01',
                        password='example', confirm='example')

    assert form.validate() is False
    assert _('Field must be between 3 and 255 characters long.') in form.full_name.errors


def test_register_form_validate_email_already_registered(user):
    """Attempt registering user with email that is already registered."""
    form = RegisterForm(username=user.email, full_name='Another Name Perhaps',
                        password='example', confirm='example')

    assert form.validate() is False
    assert _('Email already registered') in form.username.errors


# noinspection PyUnusedLocal
def test_edit_details_form_validate_username_does_not_exist(db):
    """Attempt to edit user details with a username that is not registered."""
    form = EditDetailsForm('missing@nowhere.com', username='missing@nowhere.com',
                           full_name='Mr Foo', active=choice([True, False]),
                           is_admin=choice([True, False]))

    assert form.validate() is False
    assert _('User does not exist') in form.username.errors


def test_edit_details_form_validate_modifying_username(user):
    """Attempt to edit user by giving it a new username/email."""
    form = EditDetailsForm(user.email, username='new.address@kb.se', full_name=user.full_name,
                           active=user.active, is_admin=user.is_admin)

    assert form.validate() is False
    assert _('Email cannot be modified') in form.username.errors


def test_change_password_form_validate_modifying_username(user):
    """Attempt to change password but passing in a new username/email."""
    form = ChangePasswordForm(user.email, username='new.address@kb.se',
                              password='123456', confirm='123456')

    assert form.validate() is False
    assert _('Email cannot be modified') in form.username.errors


# noinspection PyUnusedLocal
def test_register_form_validate_success(db):
    """Register user with success."""
    form = RegisterForm(username='first.last@kb.se', full_name='First Last',
                        password='example', confirm='example')

    assert form.validate() is True


def test_edit_details_form_validate_success(user):
    """Edit user details with success."""
    form = EditDetailsForm(user.email, username=user.email, full_name='My New Name',
                           active=not user.active, is_admin=not user.is_admin)

    assert form.validate() is True


def test_change_password_form_validate_success(user):
    """Change user password with success."""
    form = ChangePasswordForm(user.email, username=user.email, password='example',
                              confirm='example')

    assert form.validate() is True
