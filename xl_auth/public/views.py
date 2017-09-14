# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from ..extensions import login_manager
from ..public.forms import LoginForm
from ..user.forms import RegisterForm
from ..user.models import User
from ..utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
    login_form = LoginForm(request.form)
    # Handle logging in.
    if request.method == 'POST':
        if login_form.validate_on_submit():
            login_user(login_form.user)
            flash('You are logged in.', 'success')
            redirect_url = request.args.get('next') or url_for('user.members')
            return redirect(redirect_url)
        else:
            flash_errors(login_form)
    return render_template('public/home.html', login_form=login_form)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    register_user_form = RegisterForm(request.form)
    if register_user_form.validate_on_submit():
        User.create(email=register_user_form.username.data,
                    full_name=register_user_form.full_name.data,
                    password=register_user_form.password.data,
                    active=True)
        flash('Thank you for registering. You can now log in.', 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(register_user_form)
    return render_template('public/register.html', register_user_form=register_user_form)


@blueprint.route('/about/')
def about():
    """About page."""
    login_form = LoginForm(request.form)
    return render_template('public/about.html', login_form=login_form)
