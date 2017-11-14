# -*- coding: utf-8 -*-
"""User forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from .models import User

username = StringField(_('Email'), validators=[DataRequired(), Email(), Length(min=6, max=255)])
full_name = StringField(_('Full name'), validators=[DataRequired(), Length(min=3, max=255)])
password = PasswordField(_('Password'), validators=[DataRequired(), Length(min=6, max=64)])
confirm = PasswordField(_('Verify password'), validators=[
    DataRequired(), EqualTo('password', message=_('Passwords must match'))])


class RegisterForm(FlaskForm):
    """User registration form."""

    username = username
    full_name = full_name
    password = password
    confirm = confirm

    def __init__(self, active_user, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None
        self.active_user = active_user

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()

        if not initial_validation:
            return False

        user = User.get_by_email(self.username.data)

        if not self.active_user.is_admin:
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))

        if user:
            self.username.errors.append(_('Email already registered'))
            return False

        return True


class _EditForm(FlaskForm):
    """Edit user form."""

    username = username

    def __init__(self, active_user, target_username, *args, **kwargs):
        """Create instance."""
        super(_EditForm, self).__init__(*args, **kwargs)
        self.active_user = active_user
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
            self.username.errors.append(_('User does not exist'))
            return False

        return True


class EditDetailsForm(_EditForm):
    """Edit user details form."""

    full_name = full_name

    def validate(self):
        """Validate the form."""
        initial_validation = super(EditDetailsForm, self).validate()

        if not initial_validation:
            return False

        if self.active_user.email != self.target_username:
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))

        return True

    def set_defaults(self, user):
        """Apply 'user' attributes as field defaults."""
        self.username.default = user.email
        self.full_name.default = user.full_name
        self.process()


class AdministerForm(_EditForm):
    """Form for administering user account."""

    full_name = full_name
    is_active = BooleanField(_('Active'))
    is_admin = BooleanField(_('Administrator'))

    def validate(self):
        """Validate the form."""
        initial_validation = super(AdministerForm, self).validate()

        if not initial_validation:
            return False

        if not self.active_user.is_admin:
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))

        return True

    def set_defaults(self, user):
        """Apply 'user' attributes as field defaults."""
        self.username.default = user.email
        self.full_name.default = user.full_name
        self.is_active.default = user.is_active
        self.is_admin.default = user.is_admin
        self.process()


class ChangePasswordForm(_EditForm):
    """Change password form."""

    password = password
    confirm = confirm

    def validate(self):
        """Validate the form."""
        initial_validation = super(ChangePasswordForm, self).validate()

        if not initial_validation:
            return False

        if not self.active_user.is_admin and (self.active_user.email != self.target_username):
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))

        return True
