# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import Babel
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_oauthlib.provider import OAuth2Provider
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_static_digest import FlaskStaticDigest

bcrypt = Bcrypt()
csrf_protect = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
debug_toolbar = DebugToolbarExtension()
babel = Babel()
oauth_provider = OAuth2Provider()
flask_static_digest = FlaskStaticDigest()
