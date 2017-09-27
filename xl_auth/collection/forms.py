# -*- coding: utf-8 -*-
"""Collection forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import RadioField, StringField
from wtforms.validators import DataRequired, Length, ValidationError

from .models import Collection


class CollectionForm(FlaskForm):
    """Collection form."""

    code = StringField(_('Code'), validators=[DataRequired(), Length(min=1, max=5)])
    friendly_name = StringField(_('Name'), validators=[DataRequired(), Length(min=2, max=255)])
    category = RadioField(_('Category'), choices=[('bibliography', _('Bibliography')),
                                                  ('library', _('Library')),
                                                  ('uncategorized', _('No category'))])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(CollectionForm, self).__init__(*args, **kwargs)
        self.collection = None


class RegisterForm(CollectionForm):
    """Collection registration form."""

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()

        if not initial_validation:
            return False

        collection = Collection.query.filter_by(code=self.code.data).first()

        if collection:
            self.code.errors.append(_('Code already registered'))
            return False

        return True


class EditForm(CollectionForm):
    """Collection edit form."""

    def __init__(self, target_collection_code, *args, **kwargs):
        """Create instance."""
        super(EditForm, self).__init__(*args, **kwargs)
        self.target_collection_code = target_collection_code

    def validate_code(self, field):
        """Validate code field."""
        if field.data and field.data != self.target_collection_code:
            raise ValidationError(_('Code cannot be modified'))

    def validate(self):
        """Validate the form."""
        initial_validation = super(EditForm, self).validate()

        if not initial_validation:
            return False

        collection = Collection.query.filter_by(code=self.code.data).first()
        if not collection:
            self.code.errors.append(_('Code does not exist'))
            return False

        return True
