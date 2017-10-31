# -*- coding: utf-8 -*-
"""Test OAuth2 implementation."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for


def test_oauth_authorize_success(user, client, testapp):
    """Go to authorize page and confirm grant."""
    # Goes to authorize endpoint
    res = testapp.get('/oauth/authorize',
                      params={'client_id': client.client_id,
                              'response_type': 'code',
                              'redirect_uri': client.default_redirect_uri,
                              'scopes': client.default_scopes})
    # Redirected to homepage
    res = res.follow()
    # Fills out login form
    login_form = res.forms['loginForm']
    login_form['username'] = user.email
    login_form['password'] = 'myPrecious'
    # Submits
    res = login_form.submit().follow()
    # Sees authorization confirm form
    authorize_form = res.forms['authorizeForm']
    #assert authorize_form['client_id'] == client.client_id
    #assert authorize_form['response_type'] == 'code'  # TODO: Review us.
    #assert authorize_form['redirect_uri'] == client.default_redirect_uri
    assert authorize_form['confirm'].value == 'y'
    res = authorize_form.submit().follow()
    assert res.status_code == 200


def test_oauth_authorize_missing_client_id(user, testapp):
    """Go to authorize page without 'client_id'."""
    # Goes to authorize endpoint
    res = testapp.get(url_for('oauth.authorize'))
    # Redirected to homepage
    res = res.follow()
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    assert 'Missing+client_id+parameter.' in res.location
    # Redirected to errors page
    # Sees error
    res = res.follow()
    assert 'Missing client_id parameter.' in res


def test_oauth_authorize_invalid_client_id(user, client, testapp):
    """Go to authorize page with bad 'client_id'."""
    # Goes to authorize endpoint
    res = testapp.get('/oauth/authorize',
                      params={'client_id': 'a fake one',
                              'response_type': 'code',
                              'redirect_uri': client.default_redirect_uri})
    # Redirected to homepage
    res = res.follow()
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    assert 'Invalid+client_id+parameter+value.' in res.location
    # Redirected to errors page
    res = res.follow()
    assert 'Invalid client_id parameter value.' in res


# TODO: Add tests for response_type missing/invalid.

# TODO: Add tests for redirect_uri missing/invalid.
