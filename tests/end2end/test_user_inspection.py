"""Test inspecting user."""


from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.models import User


def test_superuser_can_inspect_user(superuser, user, testapp):
    """Inspect user details as superuser."""
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
    # Clicks Inspect button.
    res = res.click(href='/users/inspect/{0}'.format(user.id))
    # Sees inspect view.
    assert res.status_code is 200
    assert _('Inspect User \'%(email)s\'', email=user.email) in res


def test_user_cannot_inspect_any_user(user, testapp):
    """Attempt to access inspect user view."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code is 200
    res = testapp.get(url_for('user.inspect', user_id=user.id), expect_errors=True)
    # Sees error.
    assert res.status == '403 FORBIDDEN'


def test_superuser_sees_error_message_if_user_id_does_not_exist(superuser, testapp):
    """Show error when attempting to view a user that does not exist."""
    # Goes to homepage.
    res = testapp.get('/')
    # Fills out login form.
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits.
    res = form.submit().follow()
    assert res.status_code is 200
    # Fails to figures out the correct ID for another user.
    last_user = User.query.all()[-1]
    made_up_id = last_user.id + 1
    res = testapp.get(url_for('user.inspect', user_id=made_up_id)).follow()
    # Sees error message.
    assert _('User ID "%(user_id)s" does not exist', user_id=made_up_id) in res
