# -*- coding: utf-8 -*-
"""Test registering clients."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _

from xl_auth.client.models import Client


def test_superuser_can_register_new_client(superuser, testapp):
    """Register a new client."""
    old_count = len(Client.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # Clicks Clients button
    # res = res.click(href=url_for('client.home'))
    # FIXME: No nav link yet
    assert res.lxml.xpath("//a[contains(@href,'{0}')]".format(url_for('client.home'))) == []

    res = testapp.get('/clients/')
    # Clicks Register New Client button
    res = res.click(_('New Client'))

    # Fills out the form
    form = res.forms['registerForm']
    form['name'] = 'Test Client'
    form['description'] = 'Some description'
    form['redirect_uris'] = 'http://localhost/'
    form['default_scopes'] = 'read write'

    # Submits
    res = form.submit().follow()
    assert res.status_code == 200

    # A new client was created
    assert len(Client.query.all()) == old_count + 1

    # The new client is listed under existing clients
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(form['name'].value))) == 1
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(form['description'].value))) == 1


def test_user_cannot_register_client(user, collection, testapp):
    """Attempt to register a client."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # No Client home button for regular users
    assert res.lxml.xpath("//a[contains(@href,'{0}')]".format(url_for('client.home'))) == []

    # Try to go there directly
    testapp.get('/clients/', status=403)

    # Try to go directly to register
    testapp.get('/clients/register/', status=403)
