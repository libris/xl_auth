# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import lazy_gettext as _
from flask_login import login_required, login_user, logout_user

from ..extensions import login_manager
from ..public.forms import LoginForm
from ..user.models import User
from ..utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    user = User.get_by_id(int(user_id))
    return user


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
    login_form = LoginForm(request.form)
    # Handle logging in.
    if request.method == 'POST':
        if login_form.validate_on_submit():
            login_user(login_form.user)
            flash(_('You are logged in.'), 'success')
            redirect_url = request.args.get('next') or url_for('user.profile')
            return redirect(redirect_url)
        else:
            flash_errors(login_form)
    return render_template('public/home.html', login_form=login_form)


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
    login_form = LoginForm(request.form)
    return render_template('public/about.html', login_form=login_form)
