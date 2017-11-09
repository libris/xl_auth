# -*- coding: utf-8 -*-
"""Unit tests for Client model."""

from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from xl_auth.oauth.client.models import Client

from ..factories import ClientFactory


@pytest.mark.usefixtures('db', 'user')
def test_get_by_id(user):
    """Get client by ID."""
    client = Client(created_by=user.id, redirect_uris='http://example.com', default_scopes='fake')
    client.save()

    retrieved = Client.get_by_id(client.client_id)
    assert retrieved == client


@pytest.mark.usefixtures('db', 'user')
def test_factory(db, user):
    """Test user factory."""
    client = ClientFactory(created_by=user.id)
    db.session.commit()
    assert bool(client.client_id)
    assert bool(client.client_secret)
    assert bool(client.created_by)
    assert bool(client.is_confidential)
    assert bool(client.name)
    assert bool(client.description)
    assert client.default_scopes == ['read', 'write']
    assert client.redirect_uris == ['https://libris.kb.se', 'http://example.com']


@pytest.mark.usefixtures('db')
def test_client_type():
    """Test client_type."""
    confidential_client = ClientFactory()
    assert confidential_client.client_type == 'confidential'

    public_client = ClientFactory(is_confidential=False)
    assert public_client.client_type == 'public'


@pytest.mark.usefixtures('db')
def test_default_redirect_uri():
    """Test default_redirect_uri."""
    client = ClientFactory(redirect_uris='http://example.com/foo http://example.com/bar')
    expected_from_str = 'http://example.com/foo'
    assert client.default_redirect_uri == expected_from_str

    client.redirect_uris = ['http://localhost:80/', '///dev/null']
    expected_from_list = 'http://localhost:80/'
    assert client.default_redirect_uri == expected_from_list


@pytest.mark.usefixtures('db')
def test_default_scopes():
    """Test default_scopes."""
    client = ClientFactory(default_scopes='readWrite readOnly')
    assert client.default_scopes == ['readWrite', 'readOnly']

    client.default_scopes = ['read', 'write']
    assert client.default_scopes == ['read', 'write']


@pytest.mark.usefixtures('db')
def test_repr():
    """Check repr output."""
    client = ClientFactory(name='OAuth2 Client')
    assert repr(client) == '<Client({!r})>'.format('OAuth2 Client')
