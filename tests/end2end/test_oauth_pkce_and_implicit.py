"""Test OAuth2 PKCE (RFC 7636) and implicit grant (RFC 6749)."""


from base64 import b64encode, urlsafe_b64encode
from hashlib import sha256
from urllib.parse import parse_qs, urlparse

from flask import url_for

from xl_auth.oauth.grant.models import Grant
from xl_auth.oauth.token.models import Token

from ..factories import ClientFactory

CODE_VERIFIER = 'dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk'


def _s256(verifier):
    """Return S256 code_challenge for 'verifier'."""
    digest = sha256(verifier.encode('ascii')).digest()
    return urlsafe_b64encode(digest).rstrip(b'=').decode('ascii')


def _login(res, user):
    """Follow the redirect to the login page, then fill out and submit the login form."""
    res = res.follow()
    login_form = res.forms['loginForm']
    login_form['username'] = user.email
    login_form['password'] = 'myPrecious'
    return login_form.submit().follow()


def _authorize(testapp, user, **params):
    """Authorize and confirm, returning the redirect response with the code."""
    res = _login(testapp.get('/oauth/authorize', params=params), user)
    assert 'authorizeForm' in res.forms
    return res.forms['authorizeForm'].submit()


def _basic_auth(client):
    """Return Basic auth headers for 'client'."""
    credentials = '{}:{}'.format(client.client_id, client.client_secret)
    encoded = str(b64encode(credentials.encode()).decode())
    return {'Authorization': str('Basic ' + encoded)}


def _code_from_redirect(res):
    """Extract the authorization code from the redirect Location header."""
    return parse_qs(urlparse(res.location).query)['code'][0]


def test_pkce_s256_success(user, client, testapp):
    """Exchange authorization code using S256 code_verifier."""
    challenge = _s256(CODE_VERIFIER)
    res = _authorize(testapp, user, client_id=client.client_id, response_type='code',
                     redirect_uri=client.default_redirect_uri, scope='read write',
                     code_challenge=challenge, code_challenge_method='S256')
    assert res.status_code in (302, 308)

    grant = Grant.query.filter_by(client_id=client.client_id, user_id=user.id).first()
    assert grant.code_challenge == challenge
    assert grant.code_challenge_method == 'S256'

    res = testapp.post(url_for('oauth.create_access_token'),
                       params={'grant_type': 'authorization_code',
                               'code': _code_from_redirect(res),
                               'redirect_uri': grant.redirect_uri,
                               'code_verifier': CODE_VERIFIER},
                       headers=_basic_auth(client))
    assert res.status_code == 200
    token = Token.query.filter_by(client_id=client.client_id, user_id=user.id).first()
    assert res.json_body['access_token'] == token.access_token
    assert res.json_body['token_type'] == 'Bearer'
    assert res.json_body['expires_in'] == 36000


def test_pkce_plain_success(user, client, testapp):
    """Exchange authorization code using plain code_verifier."""
    res = _authorize(testapp, user, client_id=client.client_id, response_type='code',
                     redirect_uri=client.default_redirect_uri, scope='read write',
                     code_challenge=CODE_VERIFIER, code_challenge_method='plain')
    grant = Grant.query.filter_by(client_id=client.client_id, user_id=user.id).first()
    assert grant.code_challenge == CODE_VERIFIER
    assert grant.code_challenge_method == 'plain'

    res = testapp.post(url_for('oauth.create_access_token'),
                       params={'grant_type': 'authorization_code',
                               'code': _code_from_redirect(res),
                               'redirect_uri': grant.redirect_uri,
                               'code_verifier': CODE_VERIFIER},
                       headers=_basic_auth(client))
    assert res.status_code == 200
    assert Token.query.filter_by(client_id=client.client_id, user_id=user.id).first() is not None


def test_pkce_wrong_verifier_fails(user, client, testapp):
    """Wrong code_verifier is rejected with invalid_grant."""
    res = _authorize(testapp, user, client_id=client.client_id, response_type='code',
                     redirect_uri=client.default_redirect_uri, scope='read write',
                     code_challenge=_s256(CODE_VERIFIER), code_challenge_method='S256')

    res = testapp.post(url_for('oauth.create_access_token'),
                       params={'grant_type': 'authorization_code',
                               'code': _code_from_redirect(res),
                               'redirect_uri': client.default_redirect_uri,
                               'code_verifier': 'A' * 43},
                       headers=_basic_auth(client), expect_errors=True)
    assert res.status_code == 400
    assert res.json_body['error'] == 'invalid_grant'
    assert res.json_body['error_description'] == 'Code challenge failed.'


def test_authorize_without_code_challenge_fails(user, client, testapp):
    """Authorization code requests without a code_challenge are rejected."""
    res = _login(testapp.get('/oauth/authorize',
                             params={'client_id': client.client_id, 'response_type': 'code',
                                     'redirect_uri': client.default_redirect_uri,
                                     'scope': 'read write'}), user)
    assert res.status_code in (302, 308)
    assert res.location.startswith(url_for('oauth.render_errors'))
    assert "error_description=Missing+'code_challenge'." in res.location


def test_verifier_without_stored_challenge_fails(user, grant, testapp):
    """code_verifier is rejected when the grant has no stored code_challenge."""
    res = testapp.post(url_for('oauth.create_access_token'),
                       params={'grant_type': 'authorization_code',
                               'code': grant.code,
                               'redirect_uri': grant.redirect_uri,
                               'code_verifier': CODE_VERIFIER},
                       headers=_basic_auth(grant.client), expect_errors=True)
    assert res.status_code == 400
    assert res.json_body['error'] == 'invalid_request'
    assert res.json_body['error_description'] == "Missing 'code_challenge'."


def test_pkce_public_client_without_secret_succeeds(user, testapp):
    """Public client exchanges code using PKCE, without any client secret."""
    public_client = ClientFactory(is_confidential=False)
    public_client.save()

    res = _authorize(testapp, user, client_id=public_client.client_id, response_type='code',
                     redirect_uri=public_client.default_redirect_uri, scope='read write',
                     code_challenge=_s256(CODE_VERIFIER), code_challenge_method='S256')

    res = testapp.post(url_for('oauth.create_access_token'),
                       params={'grant_type': 'authorization_code',
                               'code': _code_from_redirect(res),
                               'redirect_uri': public_client.default_redirect_uri,
                               'client_id': public_client.client_id,
                               'code_verifier': CODE_VERIFIER})
    assert res.status_code == 200
    token = Token.query.filter_by(client_id=public_client.client_id, user_id=user.id).first()
    assert res.json_body['access_token'] == token.access_token


def test_public_client_without_verifier_fails(user, testapp):
    """Public client cannot exchange code without a code_verifier."""
    public_client = ClientFactory(is_confidential=False)
    public_client.save()

    res = _authorize(testapp, user, client_id=public_client.client_id, response_type='code',
                     redirect_uri=public_client.default_redirect_uri, scope='read write',
                     code_challenge=_s256(CODE_VERIFIER), code_challenge_method='S256')

    res = testapp.post(url_for('oauth.create_access_token'),
                       params={'grant_type': 'authorization_code',
                               'code': _code_from_redirect(res),
                               'redirect_uri': public_client.default_redirect_uri,
                               'client_id': public_client.client_id},
                       expect_errors=True)
    assert res.status_code == 400
    assert res.json_body['error'] == 'invalid_request'
    assert 'code_verifier' in res.json_body['error_description']


def test_confidential_client_still_requires_secret(user, client, testapp):
    """Confidential client cannot authenticate with client_id only."""
    res = _authorize(testapp, user, client_id=client.client_id, response_type='code',
                     redirect_uri=client.default_redirect_uri, scope='read write',
                     code_challenge=_s256(CODE_VERIFIER), code_challenge_method='S256')

    res = testapp.post(url_for('oauth.create_access_token'),
                       params={'grant_type': 'authorization_code',
                               'code': _code_from_redirect(res),
                               'redirect_uri': client.default_redirect_uri,
                               'client_id': client.client_id},
                       expect_errors=True)
    assert res.status_code == 401
    assert res.json_body['error'] == 'invalid_client'


def test_implicit_grant_returns_token_in_fragment(user, client, testapp):
    """Implicit grant puts the access token in the redirect URI fragment."""
    res = _authorize(testapp, user, client_id=client.client_id, response_type='token',
                     redirect_uri=client.default_redirect_uri, scope='read write',
                     state='xyz')
    assert res.status_code in (302, 308)
    assert res.location.startswith(client.default_redirect_uri)

    fragment = parse_qs(urlparse(res.location).fragment)
    token = Token.query.filter_by(client_id=client.client_id, user_id=user.id).first()
    assert fragment['access_token'][0] == token.access_token
    assert fragment['token_type'][0] == 'Bearer'
    assert int(fragment['expires_in'][0]) == 36000
    assert fragment['state'][0] == 'xyz'
    assert token.refresh_token is None

    res = testapp.get(url_for('oauth.verify'),
                      headers={'Authorization': str('Bearer ' + token.access_token)})
    assert res.status_code == 200
    assert res.json_body['user']['email'] == user.email
