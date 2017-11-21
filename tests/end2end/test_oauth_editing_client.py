# -*- coding: utf-8 -*-
"""Test editing clients."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for

from xl_auth.oauth.client.models import Client


def test_superuser_can_edit_existing_client(superuser, client, testapp):
    """Edit an existing client."""
    old_count = len(Client.query.all())
    # Check expected premises
    client_creator = client.created_by
    initial_modified_by = client.modified_by
    assert client_creator != superuser and initial_modified_by != superuser
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # Clicks Clients button
    # res = res.click(href=url_for('oauth.client.home'))
    # FIXME: No nav link yet
    assert res.lxml.xpath("//a[contains(@href,'{0}')]".format(url_for('oauth.client.home'))) == []

    res = testapp.get('/oauth/clients/')
    # Clicks Edit Client button
    res = res.click(href=url_for('oauth.client.edit', client_id=client.client_id))

    # Fills out the form
    form = res.forms['editForm']
    form['name'] = 'Test Client'
    form['description'] = 'Some description'
    form['redirect_uris'] = 'http://localhost/'
    form['default_scopes'] = 'read write'

    # Submits
    res = form.submit().follow()
    assert res.status_code == 200

    # The client was edited
    edited_client = Client.get_by_id(client.client_id)
    assert edited_client.name == form['name'].value
    assert edited_client.description == form['description'].value
    assert edited_client.redirect_uris == ['http://localhost/']
    assert edited_client.default_scopes == ['read', 'write']
    # 'modified_by' is updated to reflect change, with 'created_by' intact
    assert edited_client.created_by == client_creator
    assert edited_client.modified_by == superuser

    # No new client was created
    assert len(Client.query.all()) == old_count

    # The new client is listed under existing clients
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(form['name'].value))) == 1
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(form['description'].value))) == 1


def test_user_cannot_edit_existing_client(user, client, testapp):
    """Attempt to edit an existing client."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # No Client home button for regular users
    assert res.lxml.xpath("//a[contains(@href,'{0}')]".format(url_for('oauth.client.home'))) == []

    # Try to go there directly
    testapp.get('/oauth/clients/', status=403)

    # Try to go directly to edit
    testapp.get(url_for('oauth.client.edit', client_id=client.client_id), status=403)
