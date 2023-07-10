"""Unit tests for Token model."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta

import pytest

from xl_auth.oauth.token.models import Token

from ..factories import TokenFactory


@pytest.mark.usefixtures('db', 'user', 'client')
def test_get_by_id(user, client):
    """Get token by ID."""
    token = Token(user=user, client=client, access_token='abc', refresh_token='def', scopes='read')
    token.save()

    retrieved = token.get_by_id(token.id)
    assert retrieved == token


def test_get_all_by_user(db, user, client):
    """Get all tokens issued for a specific user."""
    token = Token(user=user, client=client, access_token='abc', refresh_token='def', scopes='read')
    token.save()
    other_token = TokenFactory()
    db.session.commit()

    user_tokens = Token.get_all_by_user(user)
    assert other_token not in user_tokens
    assert [token] == user_tokens


def test_delete_all_by_user(db, user, client):
    """Delete all tokens issued for a specific user."""
    token = Token(user=user, client=client, access_token='abc', refresh_token='def', scopes='read')
    token.save()
    other_token = TokenFactory()
    db.session.commit()

    Token.delete_all_by_user(user)
    db.session.commit()
    tokens = Token.query.all()
    assert token not in tokens
    assert [other_token] == tokens


@pytest.mark.usefixtures('db')
def test_factory(db):
    """Test token factory."""
    token = TokenFactory()
    db.session.commit()
    assert bool(token.user_id)
    assert bool(token.client_id)
    assert bool(token.access_token)
    assert bool(token.refresh_token)
    assert token.token_type == 'Bearer'
    assert bool(token.expires_at)
    assert bool(token.scopes)
    assert token.scopes == ['write', 'read']


@pytest.mark.usefixtures('db')
def test_scopes():
    """Test scopes."""
    token = TokenFactory(scopes='readWrite readOnly')
    assert token.scopes == ['readWrite', 'readOnly']

    token.scopes = ['read', 'write']
    assert token.scopes == ['read', 'write']


@pytest.mark.usefixtures('db')
def test_is_active():
    """Test is_active."""
    expired_token = TokenFactory(expires_at=datetime.utcnow() - timedelta(seconds=1))
    assert expired_token.is_active is False

    active_token = TokenFactory(expires_at=datetime.utcnow() + timedelta(seconds=10))
    assert active_token.is_active is True


@pytest.mark.usefixtures('db')
def test_repr():
    """Check repr output."""
    token = TokenFactory()
    assert repr(token) == '<Token({!r},{!r})>'.format(token.user.email, token.client.name)
