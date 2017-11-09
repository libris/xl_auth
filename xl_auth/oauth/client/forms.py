# -*- coding: utf-8 -*-
"""OAuth Client forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import DataRequired, Length, ValidationError

redirect_uris = StringField(_('Redirect URIs'), validators=[DataRequired()])
default_scopes = StringField(_('Default scopes'), validators=[DataRequired()])
is_confidential = BooleanField(_('Confidential'), default=True)
name = StringField(_('Name'), validators=[DataRequired(), Length(min=3, max=64)])
description = StringField(_('Description'), validators=[DataRequired(), Length(min=3, max=350)])


class RegisterForm(FlaskForm):
    """Client register form."""

    redirect_uris = redirect_uris
    default_scopes = default_scopes
    is_confidential = is_confidential
    name = name
    description = description

    def __init__(self, current_user, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.current_user = current_user

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()

        if not initial_validation:
            return False

        if not self.current_user.is_admin:
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))

        return True


class EditForm(FlaskForm):
    """Client edit form."""

    redirect_uris = redirect_uris
    default_scopes = default_scopes
    is_confidential = is_confidential
    name = name
    description = description

    def __init__(self, current_user, *args, **kwargs):
        """Create instance."""
        super(EditForm, self).__init__(*args, **kwargs)
        self.current_user = current_user

    def validate(self):
        """Validate the form."""
        initial_validation = super(EditForm, self).validate()

        if not initial_validation:
            return False

        if not self.current_user.is_admin:
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))

        return True

    def set_defaults(self, client):
        """Apply 'client' attributes as field defaults."""
        self.redirect_uris.default = ' '.join(client.redirect_uris)
        self.default_scopes.default = ' '.join(client.default_scopes)
        self.is_confidential.default = client.is_confidential
        self.name.default = client.name
        self.description.default = client.description
        self.process()
