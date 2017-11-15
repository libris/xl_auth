# -*- coding: utf-8 -*-
"""User views."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required

from ..utils import flash_errors
from .forms import AdministerForm, ChangePasswordForm, EditDetailsForm, RegisterForm
from .models import PasswordReset, User

blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')


@blueprint.route('/')
@login_required
def home():
    """Users landing page."""
    users_list_active = User.query.filter_by(is_active=True)
    users_list_inactive = User.query.filter_by(is_active=False)

    return render_template('users/home.html', users_list_active=users_list_active,
                           users_list_inactive=users_list_inactive)


@blueprint.route('/profile/')
@login_required
def profile():
    """Own user profile."""
    return render_template('users/profile.html', user=current_user)


@blueprint.route('/register/', methods=['GET', 'POST'])
@login_required
def register():
    """Register new user."""
    if not current_user.is_admin:
        abort(403)

    register_user_form = RegisterForm(current_user, request.form)
    if register_user_form.validate_on_submit():
        user = User(email=register_user_form.username.data,
                    full_name=register_user_form.full_name.data)
        if register_user_form.send_password_reset_email.data:
            password_reset = PasswordReset(user)
            password_reset.send_email()
            user.save()
            password_reset.save()
            flash(_('User "%(username)s" registered and emailed with a password reset link.',
                    username=user.email), 'success')
        else:
            user.save()
            flash(_('User "%(username)s" registered.', username=user.email), 'success')
        return redirect(url_for('user.home'))
    else:
        flash_errors(register_user_form)
    return render_template('users/register.html', register_user_form=register_user_form)


@blueprint.route('/administer/<int:user_id>', methods=['GET', 'POST'])
@login_required
def administer(user_id):
    """Edit user details."""
    if not current_user.is_admin:
        abort(403)

    user = User.get_by_id(user_id)
    if not user:
        flash(_('User ID "%(user_id)s" does not exist', user_id=user_id), 'danger')
        return redirect(url_for('user.home'))

    administer_form = AdministerForm(current_user, user.email, request.form)
    if administer_form.validate_on_submit():
        user.update(full_name=administer_form.full_name.data,
                    is_active=administer_form.is_active.data,
                    is_admin=administer_form.is_admin.data).save()
        flash(_('Thank you for updating user details for "%(username)s".', username=user.email),
              'success')
        return redirect(url_for('user.home'))
    else:
        administer_form.set_defaults(user)
        flash_errors(administer_form)
        return render_template('users/administer.html', administer_form=administer_form, user=user)


@blueprint.route('/edit_details/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_details(user_id):
    """Edit user details."""
    if (current_user.id != user_id) and not current_user.is_admin:
        abort(403)

    user = User.get_by_id(user_id)
    if not user:
        flash(_('User ID "%(user_id)s" does not exist', user_id=user_id), 'danger')
        return redirect(url_for('user.home'))

    edit_details_form = EditDetailsForm(current_user, user.email, request.form)
    if edit_details_form.validate_on_submit():
        user.update(full_name=edit_details_form.full_name.data).save()
        flash(_('Thank you for updating user details for "%(username)s".', username=user.email),
              'success')
        if current_user.is_admin:
            return redirect(url_for('user.home'))
        else:
            return redirect(url_for('user.profile'))
    else:
        edit_details_form.set_defaults(user)
        flash_errors(edit_details_form)
        return render_template(
            'users/edit_details.html', edit_details_form=edit_details_form, user=user)


@blueprint.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    """Change user password."""
    if (current_user.id != user_id) and not current_user.is_admin:
        abort(403)

    user = User.get_by_id(user_id)
    if not user:
        flash(_('User ID "%(user_id)s" does not exist', user_id=user_id), 'danger')
        return redirect(url_for('user.home'))

    change_password_form = ChangePasswordForm(current_user, user.email, request.form)
    if change_password_form.validate_on_submit():
        user.set_password(change_password_form.password.data)
        user.save()
        flash(_('Thank you for changing password for "%(username)s".', username=user.email),
              'success')
        if current_user.is_admin:
            return redirect(url_for('user.home'))
        else:
            return redirect(url_for('user.profile'))
    else:
        flash_errors(change_password_form)
        return render_template(
            'users/change_password.html', change_password_form=change_password_form, user=user)
