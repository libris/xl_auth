# -*- coding: utf-8 -*-
"""Test OAuth2 implementation."""

from __future__ import absolute_import, division, print_function, unicode_literals

from base64 import b64encode
from datetime import datetime, timedelta

from flask import url_for

from xl_auth import __version__
from xl_auth.grant.models import Grant
from xl_auth.token.models import Token

from ..factories import PermissionFactory


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
    # assert authorize_form['client_id'] == client.client_id
    # assert authorize_form['response_type'] == 'code'  # TODO: Review us.
    # assert authorize_form['redirect_uri'] == client.default_redirect_uri
    assert authorize_form['confirm'].value == 'y'

    # Submits confirmation and is redirected to '<redirect_uri>/?code=<grant.code>'.
    res = authorize_form.submit().follow()
    grant = Grant.query.filter_by(client_id=client.client_id, user_id=user.id).first()
    assert grant is not None
    assert res.status_code == 301
    assert res.location == client.default_redirect_uri + '/?code={}'.format(grant.code)


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
    res = testapp.get(url_for('oauth.authorize'),
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

def test_get_access_token(grant, testapp):
    """Get access token using grant code."""
    credentials = '%s:%s' % (grant.client.client_id, grant.client.client_secret)
    auth_code = str(b64encode(credentials.encode()).decode())
    res = testapp.get(url_for('oauth.create_access_token'),
                      params={'grant_type': 'authorization_code',
                              'code': grant.code,
                              'redirect_uri': grant.redirect_uri},
                      headers={'Authorization': str('Basic ' + auth_code)})

    token = Token.query.filter_by(user_id=grant.user_id, client_id=grant.client_id).first()
    assert res.json_body['scope'] == ' '.join(grant.scopes)
    assert res.json_body['token_type'] == 'Bearer'
    assert res.json_body['expires_in'] == 3600
    assert res.json_body['access_token'] == token.access_token
    assert res.json_body['refresh_token'] == token.refresh_token
    assert res.json_body['app_version'] == __version__


def test_refresh_access_token(token, testapp):
    """Get new access token using 'refresh_token'."""
    token.expires_at = datetime.utcnow() - timedelta(seconds=1)
    token.save()
    res = testapp.get(url_for('oauth.create_access_token'),
                      params={'grant_type': 'refresh_token',
                              'refresh_token': token.refresh_token,
                              'client_id': token.client.client_id,
                              'client_secret': token.client.client_secret}, expect_errors=True)

    updated_token = Token.query.filter_by(user_id=token.user_id, client_id=token.client_id).first()
    assert updated_token.id == token.id
    assert res.json_body['scope'] == ' '.join(updated_token.scopes)
    assert res.json_body['token_type'] == 'Bearer'
    assert res.json_body['expires_in'] == 3600
    assert res.json_body['access_token'] == updated_token.access_token
    assert res.json_body['access_token'] != token.access_token
    assert res.json_body['refresh_token'] == updated_token.refresh_token
    assert res.json_body['refresh_token'] != token.refresh_token
    assert res.json_body['app_version'] == __version__


def test_verify_success_response(token, testapp):
    """Get user details and token expiry."""
    permission1 = PermissionFactory(user=token.user, registrant=True, cataloger=False)
    permission1.save()

    permission2 = PermissionFactory(user=token.user, registrant=False, cataloger=True)
    permission2.save()

    res = testapp.get(url_for('oauth.verify'),
                      headers={'Authorization': str('Bearer ' + token.access_token)})

    assert res.json_body['app_version'] == __version__
    assert res.json_body['expires_at'] == token.expires_at.isoformat() + 'Z'
    assert res.json_body['user']['full_name'] == token.user.full_name
    assert res.json_body['user']['email'] == token.user.email

    assert len(res.json_body['user']['permissions']) == len(token.user.permissions)
    for permission in res.json_body['user']['permissions']:
        assert permission['code'] in {permission1.collection.code, permission2.collection.code}
        if permission['code'] == permission1.collection.code:
            assert permission['registrant'] is True
            assert permission['cataloger'] is False
        if permission['code'] == permission2.collection.code:
            assert permission['registrant'] is False
            assert permission['cataloger'] is True


def test_verify_without_bearer(testapp):
    """Attempt getting expiry and user details without 'Bearer' header."""
    res = testapp.get(url_for('oauth.verify'), expect_errors=True)

    assert res.status_code == 401
    assert res.json_body['app_version'] == __version__
    assert res.json_body['message'] == 'Bearer token not found.'


# noinspection PyUnusedLocal
def test_verify_with_invalid_bearer(db, testapp):
    """Attempt getting expiry and user details with invalid 'Bearer'."""
    res = testapp.get(url_for('oauth.verify'), expect_errors=True,
                      headers={'Authorization': str('Bearer IncorrectOne')})

    assert res.status_code == 401
    assert res.json_body['app_version'] == __version__
    assert res.json_body['message'] == 'Bearer token not found.'


def test_verify_with_expired_token(token, testapp):
    """Attempt getting expiry and user details with expired 'Bearer' token."""
    token.expires_at = datetime.utcnow() - timedelta(seconds=1)
    token.save()
    res = testapp.get(url_for('oauth.verify'), expect_errors=True,
                      headers={'Authorization': str('Bearer ' + token.access_token)})

    assert res.status_code == 401
    assert res.json_body['app_version'] == __version__
    assert res.json_body['message'] == 'Bearer token is expired.'
