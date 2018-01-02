# -*- coding: utf-8 -*-
"""Permission forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SelectField
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
    next_redirect = HiddenField('next_redirect')

    def __init__(self, current_user, *args, **kwargs):
        """Create instance."""
        super(PermissionForm, self).__init__(*args, **kwargs)
        self.current_user = current_user
        self.user_id.choices = [(-1, _('--- Select User ---'))] + [
            (user.id, user.email) for user in User.query.order_by('email').all()]

        self.collection_id.choices = [(-1, _('--- Select Collection ---'))]
        if current_user.is_admin:
            self.collection_id.choices += [
                (collection.id, collection.code)
                for collection in Collection.query.filter_by(is_active=True).order_by('code').all()
            ]
        else:
            self.collection_id.choices += sorted(
                [(permission.collection.id, permission.collection.code)
                 for permission in current_user.get_cataloging_admin_permissions()],
                key=lambda _: _[1]
            )

    # noinspection PyMethodMayBeStatic
    def validate_user_id(self, field):
        """Validate user ID is selected and exists in 'users' table."""
        if field.data == -1:
            raise ValidationError(_('A user must be selected.'))
        if not User.get_by_id(field.data):
            raise ValidationError(_('User ID "%(user_id)s" does not exist', user_id=field.data))


class RegisterForm(PermissionForm):
    """Permission registration form."""

    def set_defaults(self, user_id, collection_id):
        """Apply 'user_id' and 'collection_id' field defaults."""
        self.user_id.default = user_id
        self.collection_id.default = collection_id
        if not self.current_user.is_admin:
            self.cataloging_admin.render_kw = {'disabled': 'disabled',
                                               'title': _('Cataloging admin rights can only be '
                                                          'granted by system admins.')}
        self.process()

    def validate_collection_id(self, field):
        """Validate collection ID exists and current user may register permissions on it."""
        if field.data == -1:
            raise ValidationError(_('A collection must be selected.'))
        collection = Collection.get_by_id(field.data)
        if collection:
            if not (self.current_user.is_cataloging_admin_for(collection) or
                    self.current_user.is_admin):
                raise ValidationError(
                    _('You do not have sufficient privileges for this operation.'))
        else:
            raise ValidationError(_('Collection ID "%(collection_id)s" does not exist',
                                    collection_id=field.data))

    def validate_cataloging_admin(self, field):
        """Validate cataloging admin permissions is not set by non-admins."""
        if not self.current_user.is_admin and field.data:
            raise ValidationError(
                _('Cataloging admin rights can only be granted by system admins.'))

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False

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

    permission_id = HiddenField('permission_id', validators=[DataRequired()])

    def __init__(self, current_user, target_permission_id, *args, **kwargs):
        """Create instance."""
        super(EditForm, self).__init__(current_user, *args, **kwargs)
        self.target_permission_id = target_permission_id
        self.permission_id.validators = [AnyOf([target_permission_id])]

    def set_defaults(self, permission, new_user_id=None):
        """Apply 'permission' attributes as field defaults, maybe overridden by 'new_user_id'."""
        self.permission_id.default = permission.id
        self.user_id.default = new_user_id or permission.user_id
        self.collection_id.default = permission.collection_id
        self.registrant.default = permission.registrant
        self.cataloger.default = permission.cataloger
        self.cataloging_admin.default = permission.cataloging_admin
        if not self.current_user.is_admin and not permission.cataloging_admin:
            self.cataloging_admin.render_kw = {'disabled': 'disabled',
                                               'title': _('Cataloging admin rights can only be '
                                                          'granted by system admins.')}
        self.process()

    # noinspection PyUnusedLocal
    def validate_permission_id(self, field):
        """Validate permission ID exists and current user may edit it."""
        target_permission = Permission.get_by_id(self.target_permission_id)
        if not target_permission:
            raise ValidationError(_('Permission ID "%(permission_id)s" does not exist',
                                    permission_id=self.target_permission_id))
        current_collection = target_permission.collection
        form_collection = Collection.get_by_id(self.collection_id.data)
        if form_collection and not (self.current_user.is_cataloging_admin_for(
                current_collection, form_collection) or self.current_user.is_admin):
            raise ValidationError(_('You do not have sufficient privileges '
                                    'for this operation.'))

    # noinspection PyMethodMayBeStatic
    def validate_collection_id(self, field):
        """Validate collection ID is selected and exists in 'collections' table."""
        if field.data == -1:
            raise ValidationError(_('A collection must be selected.'))
        if not Collection.get_by_id(field.data):
            raise ValidationError(_('Collection ID "%(collection_id)s" does not exist',
                                    collection_id=field.data))

    def validate(self):
        """Validate the form."""
        initial_validation = super(EditForm, self).validate()
        if not initial_validation:
            return False

        target_permission = Permission.get_by_id(self.target_permission_id)
        current_collection = target_permission.collection
        form_collection = Collection.get_by_id(self.collection_id.data)
        if not (self.current_user.is_cataloging_admin_for(
                current_collection, form_collection) or self.current_user.is_admin):
            self.permission_id.errors.append(_('You do not have sufficient privileges '
                                               'for this operation.'))
            return False

        if self.cataloging_admin.data and target_permission.cataloging_admin is False \
                and not self.current_user.is_admin:
            self.cataloging_admin.errors.append(_('Cataloging admin rights can only be granted by '
                                                  'system admins.'))
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
