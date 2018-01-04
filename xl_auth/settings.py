# -*- coding: utf-8 -*-
"""Application configuration."""

from __future__ import absolute_import, division, print_function, unicode_literals

import os

from . import __author__, __name__, __version__


class Config(object):
    """Base configuration."""

    SERVER_NAME = os.environ.get('SERVER_NAME', None)
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'http')
    APP_NAME = __name__
    APP_VERSION = __version__
    APP_AUTHOR = __author__
    JSON_AS_ASCII = False
    SECRET_KEY = os.environ.get('XL_AUTH_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory.
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar.
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WEBPACK_MANIFEST_PATH = 'webpack/manifest.json'
    BABEL_DEFAULT_LOCALE = os.environ.get('BABEL_DEFAULT_LOCALE', 'sv')
    BABEL_DEFAULT_TIMEZONE = 'utc'
    EMAIL_DEFAULT_FROM = os.environ.get('EMAIL_DEFAULT_FROM', 'noreply@kb.se')
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.kb.se')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '25'))
    EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '5'))
    OAUTH2_PROVIDER_TOKEN_EXPIRES_IN = int(
        os.environ.get('OAUTH2_PROVIDER_TOKEN_EXPIRES_IN', 3600))
    XL_AUTH_MAX_ACTIVE_PASSWORD_RESETS = 2
    XL_AUTH_FAILED_LOGIN_TIMEFRAME = 60 * 60
    XL_AUTH_FAILED_LOGIN_MAX_ATTEMPTS = 7


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI',
                                             'postgresql://localhost/example')
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar.


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)
    DEBUG_TB_ENABLED = True
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds".
    BCRYPT_LOG_ROUNDS = 4
    WTF_CSRF_ENABLED = False  # Allows form testing.
    EMAIL_BACKEND = 'flask_emails.backends.DummyBackend'
