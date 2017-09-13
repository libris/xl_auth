# -*- coding: utf-8 -*-
"""Test registering."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for

from xl_auth.user.models import User

from ..factories import UserFactory


# noinspection PyUnusedLocal
def test_can_register(user, testapp):
    """Register a new user."""
    old_count = len(User.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Clicks Create Account button
    res = res.click('Create account')
    # Fills out the form
    form = res.forms['registerForm']
    form['email'] = 'foo@bar.com'
    form['full_name'] = 'Mr End2End'
    form['password'] = 'secret'
    form['confirm'] = 'secret'
    # Submits
    res = form.submit().follow()
    assert res.status_code == 200
    # A new user was created
    assert len(User.query.all()) == old_count + 1


# noinspection PyUnusedLocal
def test_sees_error_message_if_passwords_dont_match(user, testapp):
    """Show error if passwords don't match."""
    # Goes to registration page.
    res = testapp.get(url_for('public.register'))
    # Fills out form, but passwords don't match.
    form = res.forms['registerForm']
    form['email'] = 'foo@bar.com'
    form['full_name'] = 'Mr End2End'
    form['password'] = 'secret'
    form['confirm'] = 'secrets'
    # Submits.
    res = form.submit()
    # Sees error message.
    assert 'Passwords must match' in res


# noinspection PyUnusedLocal
def test_sees_error_message_if_user_already_registered(user, testapp):
    """Show error if user already registered."""
    user = UserFactory(active=True)  # A registered user.
    user.save()
    # Goes to registration page.
    res = testapp.get(url_for('public.register'))
    # Fills out form, but username is already registered.
    form = res.forms['registerForm']
    form['email'] = user.email
    form['full_name'] = 'Mr End2End'
    form['password'] = 'secret'
    form['confirm'] = 'secret'
    # Submits.
    res = form.submit()
    # Sees error.
    assert 'Email already registered' in res
