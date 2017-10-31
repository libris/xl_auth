# -*- coding: utf-8 -*-
"""Unit tests for Token model."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from xl_auth.token.models import Token

from ..factories import TokenFactory


@pytest.mark.usefixtures('db', 'user', 'client')
def test_get_by_id(user, client):
    """Get token by ID."""
    token = Token(user=user, client=client, access_token='abc', refresh_token='def', scopes='read')
    token.save()

    retrieved = token.get_by_id(token.id)
    assert retrieved == token


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


@pytest.mark.usefixtures('db')
def test_repr():
    """Check repr output."""
    token = TokenFactory()
    assert repr(token) == '<Token({!r},{!r})>'.format(token.user.email, token.client.name)
