"""Defines fixtures available to all tests."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
from webtest import TestApp

from xl_auth.app import create_app
from xl_auth.database import db as _db
from xl_auth.settings import TestConfig

from .factories import (ClientFactory, CollectionFactory, GrantFactory, PasswordResetFactory,
                        PermissionFactory, SuperUserFactory, TokenFactory, UserFactory)


@pytest.fixture(scope='function')
def app():
    """An application for the tests."""
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


# noinspection PyShadowingNames
@pytest.fixture(scope='function')
def testapp(app):
    """A webtest app."""
    return TestApp(app, extra_environ={'REMOTE_ADDR': str('127.0.0.1')})


# noinspection PyShadowingNames
@pytest.fixture(scope='function')
def db(app):
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection.
    _db.session.close()
    _db.drop_all()


# noinspection PyShadowingNames
@pytest.fixture
def user(db):
    """A user for the tests."""
    user = UserFactory(password='myPrecious')
    db.session.commit()
    return user


# noinspection PyShadowingNames
@pytest.fixture
def superuser(db):
    """A super user for the tests."""
    super_user = SuperUserFactory(password='myPrecious')
    db.session.commit()
    return super_user


# noinspection PyShadowingNames
@pytest.fixture
def password_reset(db):
    """A password reset for the tests."""
    password_reset = PasswordResetFactory()
    db.session.commit()
    return password_reset


# noinspection PyShadowingNames
@pytest.fixture
def collection(db):
    """A collection for the tests."""
    collection = CollectionFactory()
    db.session.commit()
    return collection


# noinspection PyShadowingNames
@pytest.fixture
def permission(db):
    """A permission for the tests."""
    permission = PermissionFactory()
    db.session.commit()
    return permission


# noinspection PyShadowingNames
@pytest.fixture
def client(db):
    """A client for the tests."""
    client = ClientFactory()
    db.session.commit()
    return client


# noinspection PyShadowingNames
@pytest.fixture
def grant(db):
    """A grant for the tests."""
    grant = GrantFactory()
    db.session.commit()
    return grant


# noinspection PyShadowingNames
@pytest.fixture
def token(db):
    """A token for the tests."""
    token = TokenFactory()
    db.session.commit()
    return token
