# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required, login_user, logout_user

from six.moves.urllib_parse import quote

from ..extensions import login_manager
from ..public.forms import ForgotPasswordForm, LoginForm, ResetPasswordForm
from ..user.models import PasswordReset, User
from ..utils import flash_errors

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
    """Home page."""
    login_form = LoginForm(request.form)
    # Handle logging in.
    if request.method == 'POST':
        if login_form.validate_on_submit():
            login_user(login_form.user)
            flash(_('You are logged in.'), 'success')
            redirect_url = login_form.next_redirect.data or url_for('user.profile')
            current_user.update_last_login()
            return redirect(redirect_url)
        else:
            flash_errors(login_form)

    return render_template('public/home.html', login_form=login_form,
                           next_redirect_url=request.args.get('next'))


@blueprint.route('/forgot_password/', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password form."""
    forgot_password_form = ForgotPasswordForm(request.form)
    if request.method == 'POST':
        if forgot_password_form.validate_on_submit():
            user = User.get_by_email(forgot_password_form.username.data)
            password_reset = PasswordReset(user)
            password_reset.save()
            # TODO: Do stuff to send out email with code.
            flash(_('This is your reset code %(code)s.', code=password_reset.code), 'success')
            # FIXME: Must be removed before deploying to prod.
            flash('Reset link: %s' % url_for('public.reset_password', email=user.email,
                                             code=password_reset.code, _external=True), 'warning')
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
        password_reset.user.save()
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
