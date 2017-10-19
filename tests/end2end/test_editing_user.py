# -*- coding: utf-8 -*-
"""Test editing existing users."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.models import User


def test_superuser_can_administer_existing_user(superuser, testapp):
    """Administer user details for an existing user."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    # Clicks Users button.
    res = res.click(_('Users'))
    # Clicks Edit Details button.
    res = res.click(_('Edit Details'))
    # Fills out the form.
    form = res.forms['administerForm']
    form['username'] = superuser.email
    form['full_name'] = 'A new name'
    form['active'].checked = not superuser.active
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200
    # The user was edited.
    edited_user = User.query.filter(User.email == superuser.email).first()
    assert edited_user.full_name == form['full_name'].value
    assert edited_user.active == form['active'].checked
    assert edited_user.is_admin == form['is_admin'].checked
    # The edited user is listed under existing users.
    assert '<td>{}</td>'.format(form['username'].value) in res
    assert '<td>{}</td>'.format(form['full_name'].value) in res
    assert '<td>{}</td>'.format(form['active'].checked) in res
    assert '<td class="bool-value-{}">{}</td>'.format(
        format(form['is_admin'].checked).lower(),
        _('Yes') if form['is_admin'].checked else _('No')
    ) in res


def test_superuser_can_change_password_for_existing_user(superuser, testapp):
    """Change password for an existing user."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    # Clicks Users button.
    res = res.click(_('Users'))
    # Clicks Change Password button.
    res = res.click(_('Change Password'))
    # Fills out the form.
    form = res.forms['changePasswordForm']
    form['username'] = superuser.email
    form['password'] = 'newSecrets13'
    form['confirm'] = 'newSecrets13'
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200
    # The user was edited.
    edited_user = User.query.filter(User.email == superuser.email).first()
    # Verify the new password is considered valid, not the old one.
    assert edited_user.check_password('myPrecious') is False
    assert edited_user.check_password('newSecrets13') is True


def test_superuser_sees_error_message_if_username_is_changed_from_administer(superuser, testapp):
    """Show error if Edit Details form modifies user username/email."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits.
    form.submit()
    # Goes to Edit Details page for current user.
    res = testapp.get(url_for('user.administer', username=superuser.email))
    # Fills out form, and changes username/email.
    form = res.forms['administerForm']
    form['username'] = 'new.one@domain.com'
    form['full_name'] = superuser.full_name
    form['active'].checked = superuser.active
    form['is_admin'].checked = superuser.is_admin
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Email'), _('Email cannot be modified')) in res


def test_superuser_sees_error_message_if_username_is_changed_from_change_password(superuser,
                                                                                  testapp):
    """Show error if Change Password form modifies user username/email."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits.
    form.submit()
    # Goes to Change Password page for current user.
    res = testapp.get(url_for('user.change_password', username=superuser.email))
    # Fills out form, and changes username/email.
    form = res.forms['changePasswordForm']
    form['username'] = 'new.one@domain.com'
    form['password'] = 'newSecrets17'
    form['confirm'] = 'newSecrets17'
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Email'), _('Email cannot be modified')) in res


def test_superuser_sees_error_message_if_full_name_is_missing_in_administer(superuser, testapp):
    """Show error if Edit Details form does not include name."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits.
    form.submit()
    # Goes to Edit Details page for current user.
    res = testapp.get(url_for('user.administer', username=superuser.email))
    # Fills out form, but omits friendly_name.
    form = res.forms['administerForm']
    form['full_name'] = ''
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Full name'), _('This field is required.')) in res


def test_superuser_sees_error_message_if_username_does_not_exist(superuser, testapp):
    """Show error when attempting Edit Details / Change Password on user that does not exist."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits.
    form.submit()
    # Goes to Edit Details page for a made-up user.
    res = testapp.get(url_for('user.administer', username='one.I.dreamt.up@gmail.com')).follow()
    # Sees error message.
    assert _('User "%(username)s" does not exist',
             username='one.I.dreamt.up@gmail.com') in res
    # Tries to open Change Password page for another made-up user.
    res = testapp.get(url_for('user.administer', username='another_fake_one@gmail.com')).follow()
    # Sees error message.
    assert _('User "%(username)s" does not exist',
             username='another_fake_one@gmail.com') in res


def test_user_cannot_administer_existing_user(superuser, user, testapp):
    """Attempt to administer user details for an existing user."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()

    # We see no Users button
    assert res.lxml.xpath("//a[contains(@text,'{0}')]".format(_('Permissions'))) == []

    # Try to go there directly
    res = testapp.get('/users/')

    # We see no Edit/Change Password buttons
    assert res.lxml.xpath("//a[contains(@text,'{0}')]".format(_('Edit'))) == []
    assert res.lxml.xpath("//a[contains(@text,'{0}')]".format(_('Change Password'))) == []

    # Try to go directly to edit
    testapp.get('/users/administer/{0}'.format(superuser.email), status=403)
    testapp.get('/users/edit_details/{0}'.format(superuser.email), status=403)


def test_user_can_edit_own_details(user, testapp):
    """Change details for self."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()

    old_name = user.full_name

    # Make sure we're on the profile page
    assert len(res.lxml.xpath("//h1[contains(., '{0} {1}')]".format(_('Welcome'),
                                                                    old_name))) == 1

    # Click on 'Edit' button
    res = res.click(_('Edit'))

    # Change name
    form = res.forms['editDetailsForm']
    form['full_name'] = 'New Name'
    res = form.submit().follow()

    # Make sure name has been updated
    assert len(res.lxml.xpath("//h1[contains(., '{0} {1}')]".format(_('Welcome'),
                                                                    old_name))) == 0
    assert len(res.lxml.xpath("//h1[contains(., '{0} New Name')]".format(_('Welcome')))) == 1
