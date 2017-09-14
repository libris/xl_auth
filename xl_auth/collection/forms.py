# -*- coding: utf-8 -*-
"""Collection forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_wtf import Form
from wtforms import PasswordField, StringField, RadioField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, AnyOf

from .models import Collection


class RegisterForm(Form):
    """Collection registration form."""

    code = StringField('Code', validators=[DataRequired(), Length(min=2, max=8)])
    friendly_name = StringField('Name', validators=[DataRequired(), Length(min=2, max=255)])
    category = RadioField('Category', choices=[('bibliography', 'Bibliography'),
                                               ('library', 'Library'),
                                               ('uncategorized', 'No category')])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.collection = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()

        if not initial_validation:
            return False

        collection = Collection.query.filter_by(code=self.code.data).first()

        if collection:
            self.code.errors.append('Code already registered')
            return False

        return True
