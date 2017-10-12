# -*- coding: utf-8 -*-
"""Permission views."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import lazy_gettext as _
from flask_login import login_required

from ..utils import flash_errors
from .forms import EditForm, RegisterForm
from .models import Permission

blueprint = Blueprint('permission', __name__, url_prefix='/permissions', static_folder='../static')


@blueprint.route('/')
@login_required
def home():
    """Permissions landing page."""
    permissions_list = Permission.query.all()
    return render_template('permissions/home.html', permissions_list=permissions_list)


@blueprint.route('/register/', methods=['GET', 'POST'])
@login_required
def register():
    """Register new permission."""
    register_permission_form = RegisterForm(request.form)
    if register_permission_form.validate_on_submit():
        permission = Permission.create(
            user_id=register_permission_form.user_id.data,
            collection_id=register_permission_form.collection_id.data,
            register=register_permission_form.register.data,
            catalogue=register_permission_form.catalogue.data,
            cataloging_admin=register_permission_form.cataloging_admin.data)
        flash(_('Added permissions for "%(username)s" on collection "%(code)s".',
                username=permission.user.email, code=permission.collection.code), 'success')
        return redirect(url_for('permission.home'))
    else:
        flash_errors(register_permission_form)
        return render_template('permissions/register.html',
                               register_permission_form=register_permission_form)


@blueprint.route('/edit/<permission_id>', methods=['GET', 'POST'])
@login_required
def edit(permission_id):
    """Edit existing permission."""
    permission = Permission.get_by_id(permission_id)
    if not permission:
        flash(_('Permission ID "%(permission_id)s" does not exist', permission_id=permission_id),
              'danger')
        return redirect(url_for('permission.home'))

    edit_permission_form = EditForm(permission_id, request.form)
    if edit_permission_form.validate_on_submit():
        permission.update(**edit_permission_form.data).save()
        flash(_('Updated permissions for "%(username)s" on collection "%(code)s".',
                username=permission.user.email, code=permission.collection.code), 'success')
        return redirect(url_for('permission.home'))
    else:
        edit_permission_form.set_defaults(permission)
        flash_errors(edit_permission_form)
        return render_template('permissions/edit.html', edit_permission_form=edit_permission_form,
                               permission=permission)


@blueprint.route('/delete/<permission_id>', methods=['GET', 'DELETE'])
@login_required
def delete(permission_id):
    """Delete existing permission."""
    permission = Permission.get_by_id(permission_id)
    if not permission:
        flash(_('Permission ID "%(permission_id)s" does not exist', permission_id=permission_id),
              'danger')
    else:
        username, collection_code = permission.user.email, permission.collection.code
        permission.delete()
        flash(_('Successfully deleted permissions for "%(username)s" on collection "%(code)s".',
                username=username, code=collection_code), 'success')
    return redirect(url_for('permission.home'))
