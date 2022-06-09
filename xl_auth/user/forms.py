# -*- coding: utf-8 -*-
"""User forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from .models import User
from xl_auth.collection.models import Collection
from ..permission.models import Permission

username = StringField(_('Email'), validators=[DataRequired(), Email(), Length(min=6, max=255)])
full_name = StringField(_('Full name'), validators=[DataRequired(), Length(min=3, max=255)])


class ApproveToSForm(FlaskForm):
    """Approve ToS form."""

    tos_approved = HiddenField(_('ToS Approved'), default='y', validators=[DataRequired()])
    next_redirect = HiddenField(validators=[DataRequired()])

    def __init__(self, user, *args, **kwargs):
        """Create instance."""
        super(ApproveToSForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate(self):
        """Validate the form."""
        initial_validation = super(ApproveToSForm, self).validate()

        if not initial_validation:
            return False

        if self.user.tos_approved_at:
            self.tos_approved.errors.append(
                _('ToS already approved at %(isoformat)s.',
                  isoformat=self.user.tos_approved_at.isoformat() + 'Z'))
            return False

        if self.tos_approved.data != 'y':
            self.tos_approved.errors.append(
                _('Invalid option "%(value)s".', value=self.tos_approved.data))
            return False

        return True


class RegisterForm(FlaskForm):
    """User registration form."""

    username = username
    full_name = full_name
    send_password_reset_email = BooleanField(_('Send password reset email'), default=True)
    next_redirect = HiddenField()

    def __init__(self, current_user, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None
        self.current_user = current_user

    # noinspection PyMethodMayBeStatic
    def validate_username(self, field):
        """Verify username does not already exist."""
        if User.get_by_email(field.data):
            raise ValidationError(_('Email already registered'))

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False

        if not (self.current_user.is_admin or self.current_user.is_cataloging_admin):
            self.username.errors.append(
                _('You do not have sufficient privileges for this operation.'))
            return False

        return True


class _EditForm(FlaskForm):
    """Edit user form."""

    username = username
    next_redirect = HiddenField()

    def __init__(self, current_user, target_username, *args, **kwargs):
        """Create instance."""
        super(_EditForm, self).__init__(*args, **kwargs)
        self.current_user = current_user
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

        if self.current_user.email != self.target_username:
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
    is_admin = BooleanField(_('System Administrator'))

    def set_defaults(self, user):
        """Apply 'user' attributes as field defaults."""
        self.username.default = user.email
        self.full_name.default = user.full_name
        self.is_active.default = user.is_active
        self.is_admin.default = user.is_admin
        self.process()

    def validate(self):
        """Validate the form."""
        initial_validation = super(AdministerForm, self).validate()

        if not initial_validation:
            return False

        if not self.current_user.is_admin:
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))

        return True


class ChangePasswordForm(_EditForm):
    """Change password form."""

    password = PasswordField(_('Password'), validators=[DataRequired(), Length(min=6, max=64)])
    confirm = PasswordField(_('Verify password'), validators=[
        DataRequired(), EqualTo('password', message=_('Passwords must match'))])

    def validate(self):
        """Validate the form."""
        initial_validation = super(ChangePasswordForm, self).validate()
        if not initial_validation:
            return False

        if not self.current_user.is_admin and (self.current_user.email != self.target_username):
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))

        return True


class ChangeEmailForm(_EditForm):
    """Change email form."""

    email = StringField(_('New email'), validators=[DataRequired(), Email(message=_("Invalid email address.")), Length(min=6, max=255)])
    confirm = StringField(_('Confirm new email'), validators=[
        DataRequired(), EqualTo('email', message=_('Email addresses must match'))])

    def validate_email(self, field):
        """Verify username does not already exist."""
        if User.get_by_email(field.data):
            raise ValidationError(_('Email already registered'))

    def validate(self):
        """Validate the form."""
        initial_validation = super(ChangeEmailForm, self).validate()
        if not initial_validation:
            return False

        if not self.current_user.is_admin and (self.current_user.email != self.target_username):
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))

        return True


class DeleteUserForm(FlaskForm):
    """Delete user form."""

    confirm = BooleanField(_('Confirm deletion'))
    next_redirect = HiddenField()

    def __init__(self, current_user, target_user, *args, **kwargs):
        super(DeleteUserForm, self).__init__(*args, **kwargs)
        self.current_user = current_user
        self.target_user = target_user

    def validate_confirm(self, field):
        """Validate that user actually clicked to confirm deletion, and that there are
        no obstacles in the way."""
        if not field.data:
            raise ValidationError(_('You must confirm deletion.'))

    def validate(self):
        """Validate the form."""

        initial_validation = super(DeleteUserForm, self).validate()
        if not initial_validation:
            return False

        if not self.current_user.is_admin:
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))
        return True
