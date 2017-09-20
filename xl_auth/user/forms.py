# -*- coding: utf-8 -*-
"""User forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import lazy_gettext as _
from flask_wtf import Form
from wtforms import PasswordField, StringField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from .models import User


username = StringField(_('Email'), validators=[DataRequired(), Email(), Length(min=6, max=255)])
full_name = StringField(_('Full name'), validators=[DataRequired(), Length(min=3, max=255)])
password = PasswordField(_('Password'), validators=[DataRequired(), Length(min=6, max=64)])
confirm = PasswordField(_('Verify password'), validators=[
    DataRequired(), EqualTo('password', message=_('Passwords must match'))])


class RegisterForm(Form):
    """User registration form."""

    username = username
    full_name = full_name
    password = password
    confirm = confirm

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()

        if not initial_validation:
            return False

        user = User.query.filter_by(email=self.username.data).first()

        if user:
            self.username.errors.append(_('Email already registered'))
            return False

        return True


class _EditForm(Form):
    """Edit user form."""

    username = username

    def __init__(self, target_username, *args, **kwargs):
        """Create instance."""
        super(_EditForm, self).__init__(*args, **kwargs)
        self.target_username = target_username

    def validate_username(self, field):
        """Validate username field."""
        if field.data and field.data != self.target_username:
            raise ValidationError(_('Email cannot be modified'))

    def validate(self):
        """Validate the form."""
        initial_validation = super(_EditForm, self).validate()

        if not initial_validation:
            return False

        user = User.query.filter_by(email=self.username.data).first()
        if not user:
            self.username.errors.append(_('Username does not exist'))
            return False

        return True


class EditDetailsForm(_EditForm):
    """Edit user details form."""

    full_name = full_name
    active = BooleanField(_('Active'))
    is_admin = BooleanField(_('Administrator'))


class ChangePasswordForm(_EditForm):
    """Change password form."""

    password = password
    confirm = confirm
