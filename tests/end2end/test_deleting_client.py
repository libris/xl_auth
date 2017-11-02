# -*- coding: utf-8 -*-
"""Test deleting clients."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for
from flask_babel import gettext as _

from xl_auth.client.models import Client


def test_superuser_can_delete_existing_client(superuser, client, testapp):
    """Delete existing client."""
    old_count = len(Client.query.all())
    name = client.name
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
    # Clicks Delete button on a client
    res = res.click(href=url_for('client.delete', client_id=client.client_id)).follow()
    assert res.status_code == 200
    # Client was deleted, so number of clients are 1 less than initial state
    assert _('Successfully deleted OAuth2 Client "%(name)s".', name=name) in res
    assert len(Client.query.all()) == old_count - 1


def test_user_cannot_delete_client(user, client, testapp):
    """Attempt to delete a client."""
    old_count = len(Client.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # We see no Clients button
    assert res.lxml.xpath("//a[contains(@text,'{0}')]".format(_('Clients'))) == []

    # Try to go there directly
    testapp.get('/clients/', status=403)

    # Try to delete
    testapp.delete(url_for('client.delete', client_id=client.client_id), status=403)

    # Nothing was deleted
    assert len(Client.query.all()) == old_count
