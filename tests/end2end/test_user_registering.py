"""Test registering user."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.models import PasswordReset, User

from ..factories import PermissionFactory, UserFactory


def test_superuser_can_register_not_triggering_password_reset(superuser, testapp):
    """Register a new user, not creating any password reset."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
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
    form['full_name'] = 'End2End'
    form['send_password_reset_email'].checked = False
    # Submits
    res = form.submit()
    assert res.status_code == 302
    assert res.location.endswith(url_for('user.home'))
    res = res.follow()
    assert res.status_code == 200
    # A new user was created
    new_user = User.get_by_email('foo@bar.com')
    assert isinstance(new_user, User)
    assert new_user.is_active is False
    # Keeping track of who created what
    assert new_user.created_by == superuser
    assert new_user.modified_by == superuser
    # A password reset was not created
    password_reset = PasswordReset.query.filter_by(user=new_user).first()
    assert password_reset is None


def test_superuser_can_register_with_password_reset(superuser, testapp):
    """Register a new user, automatically creating a password reset (for emailing)."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
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
    form['full_name'] = 'End2End'
    form['send_password_reset_email'].checked = True
    # Submits
    res = form.submit()
    assert res.status_code == 302
    assert res.location.endswith(url_for('user.home'))
    res = res.follow()
    assert res.status_code == 200
    # A new user was created
    new_user = User.get_by_email('foo@bar.com')
    assert isinstance(new_user, User)
    assert new_user.is_active is False
    assert new_user.created_by == superuser
    assert new_user.modified_by == superuser
    # A password reset was created
    password_resets = PasswordReset.query.filter_by(user=new_user).all()
    assert len(password_resets) == 1


def test_cataloging_admin_can_register_not_triggering_password_reset(user, superuser, testapp):
    """Register a new user as cataloging admin, not creating any password reset."""
    PermissionFactory(user=user, cataloging_admin=True).save_as(superuser)
    assert user.is_cataloging_admin is True
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Gets redirected to profile page
    assert _('Your Responsibilities as Cataloging Admin') in res
    # Clicks Create Account button
    res = res.click(_('New User'))
    # Fills out the form
    form = res.forms['registerUserForm']
    form['username'] = 'foo@bar.com'
    form['full_name'] = 'End2End'
    form['send_password_reset_email'].checked = False
    # Submits
    res = form.submit()
    assert res.status_code == 302
    # A new user was created
    new_user = User.get_by_email('foo@bar.com')
    assert isinstance(new_user, User)
    assert new_user.is_active is False
    # Keeping track of who created what
    assert new_user.created_by == user
    assert new_user.modified_by == user
    # A password reset was not created
    password_reset = PasswordReset.query.filter_by(user=new_user).first()
    assert password_reset is None
    # Redirect goes to detail view for the new user
    assert res.location.endswith(url_for('user.view', user_id=new_user.id))
    res = res.follow()
    assert res.status_code == 200


def test_cataloging_admin_can_register_with_password_reset(user, superuser, testapp):
    """Register a new user as cataloging admin, automatically creating a password reset."""
    PermissionFactory(user=user, cataloging_admin=True).save_as(superuser)
    assert user.is_cataloging_admin is True
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Gets redirected to profile page
    assert _('Your Responsibilities as Cataloging Admin') in res
    # Clicks Create Account button
    res = res.click(_('New User'))
    # Fills out the form
    form = res.forms['registerUserForm']
    form['username'] = 'foo@bar.com'
    form['full_name'] = 'End2End'
    form['send_password_reset_email'].checked = True
    # Submits
    res = form.submit()
    assert res.status_code == 302
    # A new user was created
    new_user = User.get_by_email('foo@bar.com')
    assert isinstance(new_user, User)
    assert new_user.is_active is False
    assert new_user.created_by == user
    assert new_user.modified_by == user
    # A password reset was created
    password_resets = PasswordReset.query.filter_by(user=new_user).all()
    assert len(password_resets) == 1
    # Redirect goes to detail view for the new user
    assert res.location.endswith(url_for('user.view', user_id=new_user.id))
    res = res.follow()
    assert res.status_code == 200


def test_user_without_cataloging_admin_permissions_can_not_register(user, testapp):
    """Attempt registering a new user without having one-or-more 'cataloging_admin' permissions."""
    assert user.is_cataloging_admin is False
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Navigate to Users
    # We see no link to Users
    assert res.lxml.xpath("//a[contains(@text,'{0}')]".format(_('Users'))) == []
    # We go there directly
    res = testapp.get('/users')
    # We see no link to Create Account
    assert res.lxml.xpath("//a[starts-with(@href,'/users/register')]") == []
    # We try to go there directly
    testapp.get('/users/register/', status=403)


def test_user_sees_error_message_if_user_already_registered(superuser, testapp):
    """Show error if user already registered."""
    user = UserFactory(is_active=True)  # A registered user.
    user.save()
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
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
    form['full_name'] = 'End2End'
    # Submits.
    res = form.submit()
    # Sees error.
    assert _('Email already registered') in res
