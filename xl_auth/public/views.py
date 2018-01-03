# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required, login_user, logout_user

from six.moves.urllib_parse import quote

from ..extensions import login_manager
from ..public.forms import ForgotPasswordForm, LoginForm, ResetPasswordForm
from ..user.models import FailedLoginAttempt, PasswordReset, User
from ..utils import flash_errors, get_redirect_target, get_remote_addr

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@login_manager.unauthorized_handler
def redirect_unauthorized():
    """Redirect to login screen."""
    return redirect(url_for('public.home') + '?next={}'.format(quote(request.full_path)))


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Root path with login form."""
    login_form = LoginForm(request.form)
    # Handle logging in.
    if request.method == 'POST':
        username = login_form.username.data
        if username and FailedLoginAttempt.too_many_recent_failures_for(username):
            abort(429)
        if login_form.validate_on_submit():
            redirect_url = get_redirect_target() or url_for('user.profile')
            login_user(login_form.user)
            current_user.update_last_login()
            if current_user.tos_approved_at:
                flash(_('You are logged in.'), 'success')
                return redirect(redirect_url)
            else:
                return redirect(
                    url_for('user.approve_tos') + '?next={}'.format(quote(redirect_url)))
        else:
            if username:
                FailedLoginAttempt(username, get_remote_addr()).save()
            flash_errors(login_form)

    return render_template('public/home.html', login_form=login_form,
                           next_redirect_url=get_redirect_target())


@blueprint.route('/forgot_password/', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password form."""
    forgot_password_form = ForgotPasswordForm(request.form)
    if request.method == 'POST':
        if forgot_password_form.validate_on_submit():
            user = User.get_by_email(forgot_password_form.username.data)
            password_reset = PasswordReset(user)
            password_reset.send_email()
            password_reset.save()
            flash(_('Password reset link sent to %(email)s.', email=user.email), 'success')
            return redirect(url_for('public.home'))
        else:
            flash_errors(forgot_password_form)

    return render_template(
        'public/forgot_password.html', forgot_password_form=forgot_password_form)


@blueprint.route('/reset_password/<string:email>/<string:code>', methods=['GET', 'POST'])
def reset_password(email, code):
    """Reset password."""
    reset_password_form = ResetPasswordForm(request.form)
    if reset_password_form.validate_on_submit():
        password_reset = PasswordReset.get_by_email_and_code(reset_password_form.username.data,
                                                             reset_password_form.code.data)
        password_reset.is_active = False
        password_reset.save()
        password_reset.user.set_password(reset_password_form.password.data)
        if not password_reset.user.is_active:
            password_reset.user.is_active = True
        password_reset.user.save_as(password_reset.user)
        flash(_('Password for "%(username)s" has been reset.',
                username=reset_password_form.username.data), 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(reset_password_form)
        return render_template('public/reset_password.html',
                               reset_password_form=reset_password_form,
                               email=email, code=code)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash(_('You are logged out.'), 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html', version=current_app.config['APP_VERSION'])
