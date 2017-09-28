# -*- coding: utf-8 -*-
"""Public forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired

from ..user.models import User


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(_('Username'), validators=[DataRequired()])
    password = PasswordField(_('Password'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter(User.email.ilike(self.username.data)).first()
        if not self.user:
            self.username.errors.append(_('Unknown username/email'))
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append(_('Invalid password'))
            return False

        if not self.user.active:
            self.username.errors.append(_('User not activated'))
            return False

        return True
