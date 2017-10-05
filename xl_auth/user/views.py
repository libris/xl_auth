# -*- coding: utf-8 -*-
"""User views."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import lazy_gettext as _
from flask_login import login_required

from ..utils import flash_errors
from .forms import ChangePasswordForm, EditDetailsForm
from .models import User

blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')


@blueprint.route('/')
@login_required
def home():
    """Users landing page."""
    users_list = User.query.all()
    return render_template('users/home.html', users_list=users_list)


@blueprint.route('/profile/')
@login_required
def profile():
    """Own user profile."""
    return render_template('users/profile.html')


@blueprint.route('/edit_details/<string:username>', methods=['GET', 'POST'])
@login_required
def edit_details(username):
    """Edit user details."""
    user = User.query.filter(User.email == username).first()
    if not user:
        flash(_('User "%(username)s" does not exist', username=username), 'danger')
        return redirect(url_for('user.home'))

    edit_details_form = EditDetailsForm(username, request.form)
    if edit_details_form.validate_on_submit():
        user.update(full_name=edit_details_form.full_name.data,
                    active=edit_details_form.active.data,
                    is_admin=edit_details_form.is_admin.data).save()
        flash(_('Thank you for updating user details for "%(username)s".', username=user.email),
              'success')
        return redirect(url_for('user.home'))
    else:
        edit_details_form.set_defaults(user)
        flash_errors(edit_details_form)
        return render_template(
            'users/edit_details.html', edit_details_form=edit_details_form, user=user)


@blueprint.route('/change_password/<string:username>', methods=['GET', 'POST'])
@login_required
def change_password(username):
    """Change user password."""
    user = User.query.filter(User.email == username).first()
    if not user:
        flash(_('User "%(username)s" does not exist', username=username), 'danger')
        return redirect(url_for('user.home'))

    change_password_form = ChangePasswordForm(username, request.form)
    if change_password_form.validate_on_submit():
        user.set_password(change_password_form.password.data)
        user.save()
        flash(_('Thank you for changing password for "%(username)s".', username=user.email),
              'success')
        return redirect(url_for('user.home'))
    else:
        flash_errors(change_password_form)
        return render_template(
            'users/change_password.html', change_password_form=change_password_form, user=user)
