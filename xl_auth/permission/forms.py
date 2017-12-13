# -*- coding: utf-8 -*-
"""Permission forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, IntegerField, SelectField
from wtforms.validators import AnyOf, DataRequired, ValidationError

from ..collection.models import Collection
from ..user.models import User
from .models import Permission


class PermissionForm(FlaskForm):
    """Permission form."""

    user_id = SelectField(_('User'), choices=[], coerce=int, validators=[DataRequired()])
    collection_id = SelectField(_('Collection'), choices=[], coerce=int,
                                validators=[DataRequired()])
    registrant = BooleanField(_('Registrant'))
    cataloger = BooleanField(_('Cataloger'))
    cataloging_admin = BooleanField(_('Cataloging Admin'))

    def __init__(self, current_user, *args, **kwargs):
        """Create instance."""
        super(PermissionForm, self).__init__(*args, **kwargs)
        self.current_user = current_user
        self.user_id.choices = [(user.id, user.email)
                                for user in User.query.order_by('email').all()]
        self.collection_id.choices = [
            (collection.id, collection.code)
            for collection in Collection.query.filter_by(is_active=True).order_by('code').all()
        ]

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

        if not self.current_user.is_admin:
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))

        permission = Permission.query.filter_by(user_id=self.user_id.data,
                                                collection_id=self.collection_id.data).first()
        if permission:
            self.user_id.errors.append(_(
                'Permissions for user "%(username)s" on collection "%(code)s" already registered',
                username=permission.user.email, code=permission.collection.code))
            return False

        return True


class EditForm(PermissionForm):
    """Permission edit form."""

    permission_id = IntegerField(_('Permission'), validators=[DataRequired()])

    def __init__(self, current_user, target_permission_id, *args, **kwargs):
        """Create instance."""
        super(EditForm, self).__init__(current_user, *args, permission_id=target_permission_id,
                                       **kwargs)
        self.target_permission_id = target_permission_id

    def set_defaults(self, permission):
        """Apply 'permission' attributes as field defaults."""
        self.user_id.default = permission.user_id
        self.collection_id.default = permission.collection_id
        self.registrant.default = permission.registrant
        self.cataloger.default = permission.cataloger
        self.cataloging_admin.default = permission.cataloging_admin
        self.process()

    def validate(self):
        """Validate the form."""
        initial_validation = super(EditForm, self).validate()

        if not initial_validation:
            return False

        if not self.current_user.is_admin:
            raise ValidationError(_('You do not have sufficient privileges for this operation.'))

        target_permission = Permission.get_by_id(self.target_permission_id)
        if not target_permission:
            self.permission_id.errors.append(_('Permission ID "%(permission_id)s" does not exist',
                                               permission_id=self.target_permission_id))
            return False

        other_permission = Permission.query.filter(
            Permission.id != target_permission.id,
            Permission.user_id == self.user_id.data,
            Permission.collection_id == self.collection_id.data
        ).first()
        if other_permission:
            self.user_id.errors.append(_(
                'Permissions for user "%(username)s" on collection "%(code)s" already registered',
                username=other_permission.user.email, code=other_permission.collection.code))
            return False

        return True


class DeleteForm(FlaskForm):
    """Permission delete form."""

    permission_id = HiddenField('permission_id', validators=[DataRequired()])
    acknowledged = HiddenField('acknowledged', default='y', validators=[AnyOf(['y'])])
    next_redirect = HiddenField('next_redirect')

    def __init__(self, current_user, target_permission_id, *args, **kwargs):
        """Create instance."""
        super(DeleteForm, self).__init__(*args, **kwargs)
        self.current_user = current_user
        self.target_permission_id = target_permission_id
        self.permission_id.default = target_permission_id
        self.permission_id.validators = [AnyOf([target_permission_id])]

    def validate_user_id(self, field):
        """Validate user ID exists in 'users' table."""
        if not User.get_by_id(field.data):
            raise ValidationError(_('User ID "%(user_id)s" does not exist', user_id=field.data))

    def validate(self):
        """Validate the form."""
        initial_validation = super(DeleteForm, self).validate()

        if not initial_validation:
            return False

        target_permission = Permission.get_by_id(self.target_permission_id)
        if target_permission:
            if self.current_user.is_admin:
                return True
            elif self.current_user.is_cataloging_admin_for(target_permission.collection):
                return True
            else:
                self.permission_id.errors.append(_('You do not have sufficient privileges for '
                                                   'this operation.'))
                return False
        else:
            self.permission_id.errors.append(_('Permission ID "%(permission_id)s" does not exist',
                                               permission_id=self.target_permission_id))
            return False
