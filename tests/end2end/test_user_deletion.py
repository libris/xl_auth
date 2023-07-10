"""Test deleting user."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.models import User


def test_superuser_can_delete_user(superuser, testapp):
    """Register a new user, and then delete the user."""
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
    # Clicks Delete User button.
    res = res.click(href='/users/delete_user/{0}'.format(new_user.id))
    # Fills out the form.
    form = res.forms['deleteUserForm']
    form['confirm'].checked = True
    # Submits.
    res = form.submit()
    # Redirected back to users' overview.
    assert res.status_code == 302
    assert res.location.endswith(url_for('user.home'))
    assert new_user.is_deleted is True
    assert new_user.email.startswith("DELETED")
    assert new_user.full_name == "DELETED"
