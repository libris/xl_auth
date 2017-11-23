# -*- coding: utf-8 -*-
"""Test editing existing users."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.models import User


def test_superuser_can_administer_existing_user(superuser, user, testapp):
    """Administer user details for an existing user."""
    # Check expected premises.
    user_creator = user.created_by
    initial_modified_by = user.modified_by
    assert user_creator != superuser and initial_modified_by != superuser
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
    res = res.click(href='/users/administer/{0}'.format(user.id))
    # Fills out the form.
    form = res.forms['administerForm']
    form['username'] = user.email
    form['full_name'] = 'A new name'
    form['is_active'].checked = not user.is_active
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200
    # The user was edited.
    edited_user = User.get_by_email(user.email)
    assert edited_user.full_name == form['full_name'].value
    assert edited_user.is_active == form['is_active'].checked
    assert edited_user.is_admin == form['is_admin'].checked
    # 'modified_by' is updated to reflect change, with 'created_by' intact
    assert edited_user.created_by == user_creator
    assert edited_user.modified_by == superuser

    # The edited user is listed under existing users.
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(form['username'].value))) == 1
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(form['full_name'].value))) == 1

    is_admin_value = format(form['is_admin'].checked).lower()
    is_admin_string = _('Yes') if form['is_admin'].checked else _('No')
    admin_xpath = "//td[@class='bool-value-{0}' and contains(., '{1}')]".format(is_admin_value,
                                                                                is_admin_string)
    assert len(res.lxml.xpath(admin_xpath)) == 1


def test_superuser_can_change_password_for_existing_user(superuser, user, testapp):
    """Change password for an existing user."""
    # Check expected premises.
    user_creator = user.created_by
    initial_modified_by = user.modified_by
    assert user_creator != superuser and initial_modified_by != superuser
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
    res = res.click(href='/users/change_password/{0}'.format(user.id))
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
    # 'modified_by' is updated to reflect change, with 'created_by' intact
    assert edited_user.created_by == user_creator
    assert edited_user.modified_by == superuser


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
    res = testapp.get(url_for('user.administer', user_id=superuser.id))
    # Fills out form, and changes username/email.
    form = res.forms['administerForm']
    form['username'] = 'new.one@domain.com'
    form['full_name'] = superuser.full_name
    form['is_active'].checked = superuser.is_active
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
    res = testapp.get(url_for('user.change_password', user_id=superuser.id))
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
    res = testapp.get(url_for('user.administer', user_id=superuser.id))
    # Fills out form, but omits friendly_name.
    form = res.forms['administerForm']
    form['full_name'] = ''
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Full name'), _('This field is required.')) in res


def test_superuser_sees_error_message_if_user_id_does_not_exist(superuser, testapp):
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
    last_user = User.query.all()[-1]
    made_up_id = last_user.id + 1
    res = testapp.get(url_for('user.administer', user_id=made_up_id)).follow()
    # Sees error message.
    assert _('User ID "%(user_id)s" does not exist', user_id=made_up_id) in res
    # Tries to open Change Password page for another made-up user.
    res = testapp.get(url_for('user.change_password', user_id=made_up_id)).follow()
    # Sees error message.
    assert _('User ID "%(user_id)s" does not exist', user_id=made_up_id) in res


def test_user_cannot_administer_other_user(superuser, user, testapp):
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
    testapp.get('/users/administer/{0}'.format(superuser.id), status=403)
    testapp.get('/users/edit_details/{0}'.format(superuser.id), status=403)
    testapp.get('/users/change_password/{0}'.format(superuser.id), status=403)


def test_user_can_edit_own_details(user, testapp):
    """Change details for self."""
    user_creator = user.created_by
    assert user_creator != user
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
    assert len(res.lxml.xpath("//h1[contains(., '{0} {1}')]".format(_('Welcome'), old_name))) == 1

    # Click on 'Edit' button
    res = res.click(_('Edit'))

    # Change name
    form = res.forms['editDetailsForm']
    form['full_name'] = 'New Name'
    res = form.submit().follow()
    # 'modified_by' is updated to reflect change, with 'created_by' intact.
    edited_user = User.get_by_email(user.email)
    assert edited_user.created_by == user_creator
    assert edited_user.modified_by == user

    # Make sure name has been updated
    assert len(res.lxml.xpath("//h1[contains(., '{0} {1}')]".format(_('Welcome'), old_name))) == 0
    assert len(res.lxml.xpath("//h1[contains(., '{0} New Name')]".format(_('Welcome')))) == 1
