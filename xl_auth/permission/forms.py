# -*- coding: utf-8 -*-
"""Permission forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField
from wtforms.validators import DataRequired, ValidationError

from ..collection.models import Collection
from ..user.models import User
from .models import Permission


class PermissionForm(FlaskForm):
    """Permission form."""

    user_id = IntegerField(_('User'), validators=[DataRequired()])
    collection_id = IntegerField(_('Collection'), validators=[DataRequired()])
    register = BooleanField(_('Registering Allowed'))
    catalogue = BooleanField(_('Cataloguing Allowed'))

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(PermissionForm, self).__init__(*args, **kwargs)

    # noinspection PyMethodMayBeStatic
    def validate_user_id(self, field):
        """Validate user ID exists in 'users' table."""
        if not User.get_by_id(field.data):
            raise ValidationError(_('User ID "%(user_id)s" does not exist', user_id=field.data))

    # noinspection PyMethodMayBeStatic
    def validate_collection_id(self, field):
        """Validate collection ID exists in 'collections' table."""
        if not Collection.get_by_id(field.data):
            raise ValidationError(
                _('Collection ID "%(collection_id)s" does not exist', collection_id=field.data))


class RegisterForm(PermissionForm):
    """Permission registration form."""

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()

        if not initial_validation:
            return False

        permission = Permission.query.filter_by(user_id=self.user_id.data,
                                                collection_id=self.collection_id.data).first()
        if permission:
            self.user_id.errors.append(_('Permissions for user ID "%(user_id)s" on collection ID '
                                         '"%(collection_id)s" already registered',
                                         user_id=permission.user.id,
                                         collection_id=permission.collection.id))
            return False

        return True


class EditForm(PermissionForm):
    """Permission edit form."""

    permission_id = IntegerField(_('Permission'), validators=[DataRequired()])

    def __init__(self, target_permission_id, *args, **kwargs):
        """Create instance."""
        super(EditForm, self).__init__(*args, permission_id=target_permission_id, **kwargs)
        self.target_permission_id = target_permission_id

    def validate(self):
        """Validate the form."""
        initial_validation = super(EditForm, self).validate()

        if not initial_validation:
            return False

        target_permission = Permission.get_by_id(self.target_permission_id)
        if not target_permission:
            self.permission_id.errors.append(_('Permission ID "%(permission_id)s" does not exist',
                                               permission_id=self.target_permission_id))
            return False

        other_permission = Permission.query.filter(
            Permission.id.isnot(target_permission.id)).filter_by(
                user_id=self.user_id.data, collection_id=self.collection_id.data).first()
        if other_permission:
            self.user_id.errors.append(_('Permissions for user ID "%(user_id)s" on collection ID '
                                         '"%(collection_id)s" already registered',
                                         user_id=other_permission.user.id,
                                         collection_id=other_permission.collection.id))
            return False

        return True
