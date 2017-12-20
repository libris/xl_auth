# -*- coding: utf-8 -*-
"""Permission views."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, abort, flash, redirect, render_template, request
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required

from six.moves.urllib_parse import quote

from ..utils import flash_errors, get_redirect_target
from .forms import DeleteForm, EditForm, RegisterForm
from .models import Permission

blueprint = Blueprint('permission', __name__, url_prefix='/permissions', static_folder='../static')


@blueprint.route('/')
@login_required
def home():
    """Permissions landing page."""
    if not current_user.is_admin:
        abort(403)

    permissions_list = Permission.query.all()
    return render_template('permissions/home.html', permissions_list=permissions_list)


@blueprint.route('/register/', methods=['GET', 'POST'],
                 defaults={'user_id': None, 'collection_id': None})
@blueprint.route('/register/user/<user_id>', methods=['GET', 'POST'],
                 defaults={'collection_id': None})
@blueprint.route('/register/collection/<collection_id>', methods=['GET', 'POST'],
                 defaults={'user_id': None})
@login_required
def register(user_id, collection_id):
    """Register new permission."""
    if not (current_user.is_admin or current_user.is_cataloging_admin):
        abort(403)

    register_permission_form = RegisterForm(current_user, request.form)
    if request.method == 'POST':
        if register_permission_form.validate_on_submit():
            permission = Permission.create_as(
                current_user,
                user_id=register_permission_form.user_id.data,
                collection_id=register_permission_form.collection_id.data,
                registrant=register_permission_form.registrant.data,
                cataloger=register_permission_form.cataloger.data,
                cataloging_admin=register_permission_form.cataloging_admin.data)
            flash(_('Added permissions for "%(username)s" on collection "%(code)s".',
                    username=permission.user.email, code=permission.collection.code), 'success')
            return redirect(get_redirect_target())
        else:
            flash_errors(register_permission_form)

    register_permission_form.set_defaults(user_id, collection_id)
    return render_template('permissions/register.html',
                           register_permission_form=register_permission_form,
                           full_path_quoted=quote(request.full_path),
                           next_redirect_url=get_redirect_target())


@blueprint.route('/edit/<permission_id>', methods=['GET', 'POST'])
@login_required
def edit(permission_id):
    """Edit existing permission."""
    if not (current_user.is_admin or current_user.is_cataloging_admin):
        abort(403)

    permission = Permission.get_by_id(permission_id)
    if not permission:
        flash(_('Permission ID "%(permission_id)s" does not exist', permission_id=permission_id),
              'danger')
        return redirect(get_redirect_target())

    edit_permission_form = EditForm(current_user, permission_id, request.form)
    if request.method == 'POST':
        if edit_permission_form.validate_on_submit():
            permission.update_as(current_user, **edit_permission_form.data)
            flash(_('Updated permissions for "%(username)s" on collection "%(code)s".',
                    username=permission.user.email, code=permission.collection.code), 'success')
            return redirect(get_redirect_target())
        else:
            flash_errors(edit_permission_form)

    edit_permission_form.set_defaults(permission)
    return render_template('permissions/edit.html', permission=permission,
                           edit_permission_form=edit_permission_form,
                           full_path_quoted=quote(request.full_path),
                           next_redirect_url=request.args.get('next'))


@blueprint.route('/delete/<permission_id>', methods=['GET', 'POST'])
@login_required
def delete(permission_id):
    """Delete existing permission."""
    if not (current_user.is_admin or current_user.is_cataloging_admin):
        abort(403)

    permission = Permission.get_by_id(permission_id)
    if not permission:
        flash(_('Permission ID "%(permission_id)s" does not exist', permission_id=permission_id),
              'danger')
        return redirect(get_redirect_target())

    delete_permission_form = DeleteForm(current_user, permission_id, request.form)
    if request.method == 'POST':
        if delete_permission_form.validate_on_submit():
            username, collection_code = permission.user.email, permission.collection.code
            permission.delete()
            flash(_('Successfully deleted permissions for "%(username)s" on collection '
                    '"%(code)s".', username=username, code=collection_code), 'success')
            return redirect(get_redirect_target())
        else:
            flash_errors(delete_permission_form)

    return render_template('permissions/delete.html', permission=permission,
                           delete_permission_form=delete_permission_form,
                           next_redirect_url=get_redirect_target())
