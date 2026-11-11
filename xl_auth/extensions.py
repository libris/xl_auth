"""Extensions module. Each extension is initialized in the app factory located in app.py."""


from authlib.integrations.flask_oauth2 import AuthorizationServer as _AuthorizationServer
from authlib.integrations.flask_oauth2 import ResourceProtector as _ResourceProtector
from authlib.integrations.flask_oauth2.requests import FlaskOAuth2Request
from authlib.oauth2.rfc6749 import MissingAuthorizationError
from flask import current_app, jsonify
from flask import request
from flask import request as flask_request
from flask_babel import Babel
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_static_digest import FlaskStaticDigest
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import Unauthorized

bcrypt = Bcrypt()
csrf_protect = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
babel = Babel()
flask_static_digest = FlaskStaticDigest()


class OAuth2Request(FlaskOAuth2Request):
    """OAuth2 request that also reads token endpoint parameters from the query string."""

    @property
    def form(self):
        """Return merged query string and form body parameters."""
        # TODO: Kept for legacy flask-oauthlib-era clients. Accepting token endpoint
        # parameters (incl. 'client_secret' and 'refresh_token') from the query string,
        # combined with the '/oauth/token' route and grant classes allowing GET,
        # exposes credentials in access logs and browser history. Restrict the token
        # endpoint to POST body-only parameters once legacy clients have migrated.
        return self._request.values


class AuthorizationServer(_AuthorizationServer):
    """Authorization server creating query-string aware OAuth2 requests."""

    def create_oauth2_request(self, request):
        """Create OAuth2Request for the current Flask request."""
        return OAuth2Request(flask_request)


class ResourceProtector(_ResourceProtector):
    """Resource protector keeping the legacy 'request.oauth' and JSON error responses."""

    def acquire_token(self, scopes=None, **kwargs):
        """Acquire token and attach it to 'request.oauth'."""
        token = super(ResourceProtector, self).acquire_token(scopes, **kwargs)
        request.oauth = token
        return token

    def raise_error_response(self, error):
        """Raise legacy JSON error response for OAuth2Error."""
        if isinstance(error, MissingAuthorizationError):
            message, status_code = 'Bearer token not found.', 401
        else:
            message, status_code = error.get_error_description(), error.status_code
        response = jsonify(app_version=current_app.config['APP_VERSION'], message=message)
        response.status_code = status_code
        raise Unauthorized(response=response)


oauth_server = AuthorizationServer()
require_oauth = ResourceProtector()
