# -*- coding: utf-8 -*-
"""Test inspecting user."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _


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
