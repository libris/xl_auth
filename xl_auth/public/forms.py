# -*- coding: utf-8 -*-
"""Public forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField
from wtforms.validators import DataRequired, EqualTo, Length

from ..user.models import PasswordReset, User


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(_('Username'), validators=[DataRequired()])
    password = PasswordField(_('Password'), validators=[DataRequired()])
    next_redirect = HiddenField()

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.get_by_email(self.username.data)
        if not self.user:
            self.username.errors.append(_('Unknown username/email'))
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append(_('Invalid password'))
            return False

        if not self.user.is_active:
            self.username.errors.append(_('User not activated'))
            return False

        return True


class ForgotPasswordForm(FlaskForm):
    """Reset password form."""

    username = StringField(_('Email'), validators=[DataRequired()])

    def validate(self):
        """Validate the form."""
        initial_validation = super(ForgotPasswordForm, self).validate()

        if not initial_validation:
            return False

        user = User.get_by_email(self.username.data)
        if user:
            active_resets = PasswordReset.get_active_resets_for_email(user.email)
            recent_active_resets = [reset for reset in active_resets if
                                    reset.modified_at > (datetime.utcnow() - timedelta(hours=2))]
            if len(recent_active_resets) >= PasswordReset.MAX_ALLOWED_ACTIVE_PASSWORD_RESETS:
                self.username.errors.append(_('You already have an active password reset. Please '
                                              'check your email inbox (and your Spam folder) or '
                                              'try again later.'))
                return False
            else:
                return True
        else:
            self.username.errors.append(_('Unknown username/email'))
            return False


class ResetPasswordForm(FlaskForm):
    """Reset password form."""

    code = HiddenField(validators=[DataRequired()])
    username = StringField(_('Email'), validators=[DataRequired()])
    password = PasswordField(_('Password'), validators=[DataRequired(), Length(min=6, max=64)])
    confirm = PasswordField(_('Verify password'),
                            validators=[DataRequired(),
                                        EqualTo('password', message=_('Passwords must match'))])

    def validate(self):
        """Validate the form."""
        initial_validation = super(ResetPasswordForm, self).validate()

        if not initial_validation:
            return False

        password_reset = PasswordReset.get_by_email_and_code(self.username.data, self.code.data)
        if password_reset:  # Implies there was also a matching user.
            if password_reset.expires_at < datetime.utcnow():
                self.code.errors.append(_('Reset code "%(code)s" expired at %(isoformat)s',
                                          code=self.code.data,
                                          isoformat=password_reset.expires_at.isoformat() + 'Z'))
                return False
            if not password_reset.is_active:
                self.code.errors.append(_('Reset code "%(code)s" already used (%(isoformat)s)',
                                          code=self.code.data,
                                          isoformat=password_reset.modified_at.isoformat() + 'Z'))
                return False
            return True
        else:
            self.code.errors.append(_('Reset code "%(code)s" does not exit', code=self.code.data))
            return False
