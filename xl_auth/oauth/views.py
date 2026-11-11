"""OAuth2 views."""


from datetime import datetime, timedelta

from authlib.oauth2 import OAuth2Error
from authlib.oauth2.rfc6749 import InvalidRequestError, grants
from authlib.oauth2.rfc6750 import BearerTokenValidator
from authlib.oauth2.rfc6750.errors import InsufficientScopeError, InvalidTokenError
from authlib.oauth2.rfc7009 import RevocationEndpoint
from authlib.oauth2.rfc7636 import CodeChallenge
from flask import (Blueprint, current_app, json, jsonify, redirect, render_template, request,
                   session, url_for)
from flask_login import current_user, login_required

from ..extensions import csrf_protect, oauth_server, require_oauth
from ..user.models import User
from .client.models import Client
from .forms import AuthorizeForm
from .grant.models import Grant
from .token.models import Token

blueprint = Blueprint('oauth', __name__, url_prefix='/oauth', static_folder='../static')


def query_client(client_id):
    """Return Client object."""
    return Client.get_by_id(client_id)


def save_token(new_token, request_):
    """Create or update Token object."""
    expires_at = datetime.utcnow() + timedelta(seconds=new_token.get('expires_in', 36000))
    grant_type = request_.payload.grant_type

    if grant_type == 'refresh_token':
        token = Token.query.filter_by(client_id=request_.client.client_id,
                                      user_id=request_.user.id,
                                      refresh_token=request_.form.get('refresh_token')).first()
        token.access_token = new_token['access_token']
        token.refresh_token = new_token['refresh_token']
        token.expires_at = expires_at
    else:
        user_id = request_.user.id if request_.user else None
        if grant_type == 'client_credentials':
            if not request_.client.user_id:
                # TODO: this should ideally happen before the call to save_token.
                raise OAuth2Error(error='invalid_request', status_code=400,
                                  description='No user bound to client')
            user_id = request_.client.user_id

        token = Token(
            access_token=new_token['access_token'],
            refresh_token=new_token.get('refresh_token', None),
            token_type=new_token['token_type'],
            scopes=new_token['scope'],
            expires_at=expires_at,
            client_id=request_.client.client_id,
            user_id=user_id
        )

    return token.save()


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    """Authorization code grant with mandatory PKCE, backed by the Grant model."""

    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post', 'none']
    TOKEN_ENDPOINT_HTTP_METHODS = ['POST', 'GET']

    def save_authorization_code(self, code, request):
        """Create Grant object."""
        expires_at = None
        return Grant(
            client_id=request.client.client_id,
            code=code,
            redirect_uri=request.payload.redirect_uri or request.client.default_redirect_uri,
            scopes=request.scope,
            user_id=request.user.id,
            code_challenge=request.payload.data.get('code_challenge'),
            code_challenge_method=request.payload.data.get('code_challenge_method'),
            expires_at=expires_at
        ).save()

    def query_authorization_code(self, code, client):
        """Return Grant object if valid."""
        item = Grant.query.filter_by(client_id=client.client_id, code=code).first()
        if item and not item.is_expired():
            return item
        return None

    def delete_authorization_code(self, authorization_code):
        """Delete Grant object."""
        authorization_code.delete()

    def authenticate_user(self, authorization_code):
        """Return user bound to Grant object."""
        return authorization_code.user


def _authenticate_implicit_client(query_client, request):
    """Identify implicit-grant client by client_id only, without client secret."""
    client_id = request.payload.client_id
    if client_id and not request.payload.data.get('client_secret'):
        return query_client(client_id)
    return None


class MandatoryCodeChallenge(CodeChallenge):
    """PKCE extension requiring a code challenge for every authorization code request."""

    def validate_code_challenge(self, grant, redirect_uri):
        """Require 'code_challenge' in the authorization request."""
        if not grant.request.payload.data.get('code_challenge'):
            raise InvalidRequestError("Missing 'code_challenge'.")
        super(MandatoryCodeChallenge, self).validate_code_challenge(grant, redirect_uri)

    def validate_code_verifier(self, grant, result):
        """Require a stored code challenge when exchanging an authorization code."""
        authorization_code = grant.request.authorization_code
        if not self.get_authorization_code_challenge(authorization_code):
            raise InvalidRequestError("Missing 'code_challenge'.")
        super(MandatoryCodeChallenge, self).validate_code_verifier(grant, result)


class ImplicitGrant(grants.ImplicitGrant):
    """Implicit grant returning access tokens in the redirect URI fragment."""

    TOKEN_ENDPOINT_AUTH_METHODS = ['implicit_client']


class ClientCredentialsGrant(grants.ClientCredentialsGrant):
    """Client credentials grant binding tokens to the client's user."""

    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post']
    TOKEN_ENDPOINT_HTTP_METHODS = ['POST', 'GET']

    def create_token_response(self):
        """Issue token including refresh token, like the legacy implementation."""
        token = self.generate_token(scope=self.request.payload.scope,
                                    include_refresh_token=True)
        self.save_token(token)
        return 200, token, self.TOKEN_RESPONSE_HEADER


class RefreshTokenGrant(grants.RefreshTokenGrant):
    """Refresh token grant rotating tokens in place."""

    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post']
    TOKEN_ENDPOINT_HTTP_METHODS = ['POST', 'GET']
    INCLUDE_NEW_REFRESH_TOKEN = True

    def authenticate_refresh_token(self, refresh_token):
        """Return Token object."""
        return Token.query.filter_by(refresh_token=refresh_token).first()

    def authenticate_user(self, credential):
        """Return user bound to Token object."""
        return credential.user

    def revoke_old_credential(self, credential):
        """Keep Token row; it is updated in place by 'save_token'."""
        pass


class Revocation(RevocationEndpoint):
    """Token revocation endpoint, also authenticating clients without a secret."""

    CLIENT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post', 'none']

    def query_token(self, token_string, token_type_hint):
        """Return Token object."""
        if token_type_hint == 'refresh_token':
            return Token.query.filter_by(refresh_token=token_string).first()
        token = Token.query.filter_by(access_token=token_string).first()
        if not token:
            token = Token.query.filter_by(refresh_token=token_string).first()
        return token

    def revoke_token(self, token, request):
        """Delete Token object."""
        token.delete()


class BearerValidator(BearerTokenValidator):
    """Bearer token validator with the legacy error messages."""

    def authenticate_token(self, token_string):
        """Return Token object."""
        return Token.query.filter_by(access_token=token_string).first()

    def validate_token(self, token, scopes, request):
        """Validate Token object."""
        if not token:
            raise InvalidTokenError(description='Bearer token not found.')
        if token.is_expired():
            raise InvalidTokenError(description='Bearer token is expired.')
        if self.scope_insufficient(token.get_scope(), scopes):
            raise InsufficientScopeError()


oauth_server.register_client_auth_method('implicit_client', _authenticate_implicit_client)
oauth_server.register_grant(AuthorizationCodeGrant, [MandatoryCodeChallenge()])
oauth_server.register_grant(ImplicitGrant)
oauth_server.register_grant(ClientCredentialsGrant)
oauth_server.register_grant(RefreshTokenGrant)
oauth_server.register_endpoint(Revocation)
require_oauth.register_token_validator(BearerValidator())


def init_app(app):
    """Initialize the OAuth2 server for 'app'."""
    oauth_server.init_app(app, query_client=query_client, save_token=save_token)


def _authorize_error_description(error):
    """Map OAuth2Error to the legacy authorize error description."""
    client_id = request.values.get('client_id')
    if not client_id:
        return 'Missing client_id parameter.'
    if not query_client(client_id):
        return 'Invalid client_id parameter value.'
    return error.get_error_description()


def _already_authorized(client_id, scopes):
    """Whether `client_id` was already granted (at least) `scopes` this session."""
    authorized = session.get('authorized_scopes', {})
    return set(scopes).issubset(set(authorized.get(client_id, [])))


def _remember_authorization(client_id, scopes):
    """Record in-session consent for `client_id` covering (at least) `scopes`."""
    authorized = session.get('authorized_scopes', {})
    previously = set(authorized.get(client_id, []))
    authorized[client_id] = sorted(previously | set(scopes))
    session['authorized_scopes'] = authorized


@blueprint.route('/authorize', methods=['GET', 'POST'])
@login_required
def authorize():
    """OAuth2'orize."""
    try:
        consent_grant = oauth_server.get_consent_grant()
    except OAuth2Error as error:
        return redirect(url_for('oauth.render_errors', error=error.error,
                                error_description=_authorize_error_description(error)))

    authorize_form = AuthorizeForm(request.form)
    client_id = consent_grant.client.client_id
    scopes = (request.values.get('scope') or '').split()

    if request.method == 'GET':
        if _already_authorized(client_id, scopes):
            return oauth_server.create_authorization_response(
                grant=consent_grant, grant_user=current_user)
        return render_template('oauth/authorize.html', authorize_form=authorize_form,
                               client=consent_grant.client, scopes=scopes)

    confirm = authorize_form['confirm'].data == 'y'
    if confirm:
        _remember_authorization(client_id, scopes)
    return oauth_server.create_authorization_response(
        grant=consent_grant, grant_user=current_user if confirm else None)


@csrf_protect.exempt
@blueprint.route('/token', methods=['POST', 'GET'])
def create_access_token():
    """Generate access token."""
    response = oauth_server.create_token_response()
    if response.status_code == 200:
        body = json.loads(response.get_data(as_text=True))
        body['app_version'] = current_app.config['APP_VERSION']
        response.set_data(json.dumps(body))
    return response


@blueprint.route('/verify', methods=['GET'])
@require_oauth(['read', 'write'])
def verify():
    """Verify access token is valid and return a bunch of user details."""
    oauth = request.oauth
    assert isinstance(oauth.user, User)

    return jsonify(
        app_version=current_app.config['APP_VERSION'],
        expires_at=oauth.expires_at.isoformat() + 'Z',
        user={
            'full_name': oauth.user.full_name,
            'email': oauth.user.email,
            'id': oauth.user.id,
            'permissions': [{'code': permission.collection.code,
                             'friendly_name': permission.collection.friendly_name,
                             'cataloger': permission.cataloger,
                             'registrant': permission.registrant,
                             'global_registrant': permission.global_registrant}
                            for permission in oauth.user.permissions
                            if permission.collection.is_active]
        }
    )


@blueprint.route('/revoke', methods=['POST'])
@login_required
def revoke_access_token():
    """Revoke access token."""
    return oauth_server.create_endpoint_response('revocation')


@blueprint.route('/errors', methods=['GET'])
def render_errors():
    """Render OAuth2 errors."""
    return render_template('oauth/errors.html', **request.args)
