# -*- coding: utf-8 -*-
"""Test registering user."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.models import User

from ..factories import UserFactory


# noinspection PyUnusedLocal
def test_user_can_register(superuser, testapp):
    """Register a new user."""
    old_count = len(User.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form in navbar
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Navigate to Users
    res = res.click(_('Users'))
    # Clicks Create Account button
    res = res.click(_('New User'))
    # Fills out the form
    form = res.forms['registerUserForm']
    form['username'] = 'foo@bar.com'
    form['full_name'] = 'Mr End2End'
    form['password'] = 'secret'
    form['confirm'] = 'secret'
    # Submits
    res = form.submit().follow()
    assert res.status_code == 200
    # A new user was created
    assert len(User.query.all()) == old_count + 1


# noinspection PyUnusedLocal
def test_user_sees_error_message_if_passwords_dont_match(superuser, user, testapp):
    """Show error if passwords don't match."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form in navbar
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    form.submit().follow()
    # Goes to registration page.
    res = testapp.get(url_for('user.register'))
    # Fills out form, but passwords don't match.
    form = res.forms['registerUserForm']
    form['username'] = 'foo@bar.com'
    form['full_name'] = 'Mr End2End'
    form['password'] = 'secret'
    form['confirm'] = 'secrets'
    # Submits.
    res = form.submit()
    # Sees error message.
    assert _('Passwords must match') in res


# noinspection PyUnusedLocal
def test_user_sees_error_message_if_user_already_registered(superuser, user, testapp):
    """Show error if user already registered."""
    user = UserFactory(active=True)  # A registered user.
    user.save()
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form in navbar
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    form.submit().follow()
    # Goes to registration page.
    res = testapp.get(url_for('user.register'))
    # Fills out form, but username is already registered.
    form = res.forms['registerUserForm']
    form['username'] = user.email.upper()  # Default would be `userN@example.com`, not upper-cased.
    form['full_name'] = 'Mr End2End'
    form['password'] = 'secret'
    form['confirm'] = 'secret'
    # Submits.
    res = form.submit()
    # Sees error.
    assert _('Email already registered') in res
