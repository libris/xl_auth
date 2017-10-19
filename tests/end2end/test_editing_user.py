# -*- coding: utf-8 -*-
"""Test editing existing users."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.models import User


def test_user_can_edit_details_for_existing_user(user, testapp):
    """Edit user details for an existing user."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form in navbar.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    # Clicks Users button.
    res = res.click(_('Users'))
    # Clicks Edit Details button.
    res = res.click(href='/users/edit_details/' + user.email.replace('@', '%40'))
    # Fills out the form.
    form = res.forms['editDetailsForm']
    form['username'] = user.email
    form['full_name'] = 'A new name'
    form['active'].checked = not user.active
    form['is_admin'].checked = not user.is_admin
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200
    # The user was edited.
    edited_user = User.query.filter(User.email == user.email).first()
    assert edited_user.full_name == form['full_name'].value
    assert edited_user.active == form['active'].checked
    assert edited_user.is_admin == form['is_admin'].checked
    # The edited user is listed under existing users.
    assert '<td>{}</td>'.format(form['username'].value) in res
    assert '<td>{}</td>'.format(form['full_name'].value) in res
    assert '<td class="bool-value-{}">{}</td>'.format(
        format(form['is_admin'].checked).lower(),
        _('Yes') if form['is_admin'].checked else _('No')
    ) in res


def test_user_can_change_password_for_existing_user(user, testapp):
    """Change password for an existing user."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form in navbar.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    # Clicks Users button.
    res = res.click(_('Users'))
    # Clicks Change Password button.
    res = res.click(href='/users/change_password/' + user.email.replace('@', '%40'))
    # Fills out the form.
    form = res.forms['changePasswordForm']
    form['username'] = user.email
    form['password'] = 'newSecrets13'
    form['confirm'] = 'newSecrets13'
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200
    # The user was edited.
    edited_user = User.query.filter(User.email == user.email).first()
    # Verify the new password is considered valid, not the old one.
    assert edited_user.check_password('myPrecious') is False
    assert edited_user.check_password('newSecrets13') is True


def test_user_sees_error_message_if_username_is_changed_from_edit_details(user, testapp):
    """Show error if Edit Details form modifies user username/email."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form in navbar.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    form.submit()
    # Goes to Edit Details page for current user.
    res = testapp.get(url_for('user.edit_details', username=user.email))
    # Fills out form, and changes username/email.
    form = res.forms['editDetailsForm']
    form['username'] = 'new.one@domain.com'
    form['full_name'] = user.full_name
    form['active'].checked = user.active
    form['is_admin'].checked = user.is_admin
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Email'), _('Email cannot be modified')) in res


def test_user_sees_error_message_if_username_is_changed_from_change_password(user, testapp):
    """Show error if Change Password form modifies user username/email."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form in navbar.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    form.submit()
    # Goes to Change Password page for current user.
    res = testapp.get(url_for('user.change_password', username=user.email))
    # Fills out form, and changes username/email.
    form = res.forms['changePasswordForm']
    form['username'] = 'new.one@domain.com'
    form['password'] = 'newSecrets17'
    form['confirm'] = 'newSecrets17'
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Email'), _('Email cannot be modified')) in res


def test_user_sees_error_message_if_full_name_is_missing_in_edit_details(user, testapp):
    """Show error if Edit Details form does not include name."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form in navbar.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    form.submit()
    # Goes to Edit Details page for current user.
    res = testapp.get(url_for('user.edit_details', username=user.email))
    # Fills out form, but omits friendly_name.
    form = res.forms['editDetailsForm']
    form['full_name'] = ''
    form['active'].checked = user.active
    form['is_admin'].checked = user.is_admin
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Full name'), _('This field is required.')) in res


def test_user_sees_error_message_if_username_does_not_exist(user, testapp):
    """Show error when attempting Edit Details / Change Password on user that does not exist."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form in navbar.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    form.submit()
    # Goes to Edit Details page for a made-up user.
    res = testapp.get(url_for('user.edit_details', username='one.I.dreamt.up@gmail.com')).follow()
    # Sees error message.
    assert _('User "%(username)s" does not exist',
             username='one.I.dreamt.up@gmail.com') in res
    # Tries to open Change Password page for another made-up user.
    res = testapp.get(url_for('user.edit_details', username='another_fake_one@gmail.com')).follow()
    # Sees error message.
    assert _('User "%(username)s" does not exist',
             username='another_fake_one@gmail.com') in res
