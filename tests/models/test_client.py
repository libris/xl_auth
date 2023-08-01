"""Unit tests for Client model."""


from datetime import datetime

import pytest

from xl_auth.oauth.client.models import Client
from xl_auth.user.models import User

from ..factories import ClientFactory, SuperUserFactory


def test_get_by_id(superuser):
    """Get client by ID."""
    client = Client(name='favv', description='favorite client', redirect_uris='http://example.com',
                    default_scopes='fake')
    client.save_as(superuser)

    retrieved = Client.get_by_id(client.client_id)
    assert retrieved == client


def test_created_by_and_modified_by_is_updated(superuser):
    """Test created/modified by."""
    client = Client(name='favv', description='favorite client', redirect_uris='http://example.com',
                    default_scopes='fake')
    client.save_as(superuser)
    assert client.created_by_id == superuser.id
    assert client.created_by == superuser
    assert client.modified_by_id == superuser.id
    assert client.modified_by == superuser

    # Another superuser updates something in the client.
    another_superuser = SuperUserFactory()
    client.update_as(another_superuser, commit=True, default_scopes='another')
    assert client.created_by == superuser
    assert client.modified_by == another_superuser


def test_created_at_defaults_to_datetime(superuser):
    """Test creation date."""
    client = Client(name='favv', description='favorite client', redirect_uris='http://example.com',
                    default_scopes='fake')
    client.save_as(superuser)

    assert bool(client.created_at)
    assert isinstance(client.created_at, datetime)


def test_modified_at_defaults_to_current_datetime(superuser):
    """Test modified date."""
    client = Client(name='favv', description='favorite client', redirect_uris='http://example.com',
                    default_scopes='fake')
    client.save_as(superuser)
    first_modified_at = client.modified_at

    assert abs((first_modified_at - client.created_at).total_seconds()) < 10

    client.is_confidential = not client.is_confidential
    client.save()

    assert first_modified_at != client.modified_at


def test_factory(db):
    """Test user factory."""
    client = ClientFactory()
    db.session.commit()
    assert bool(client.client_id)
    assert bool(client.client_secret)
    assert bool(client.is_confidential)
    assert client.default_scopes == ['read', 'write']
    assert client.redirect_uris == ['https://libris.kb.se', 'http://example.com']
    assert bool(client.name)
    assert bool(client.description)

    assert isinstance(client.modified_at, datetime)
    assert isinstance(client.modified_by, User)
    assert isinstance(client.created_at, datetime)
    assert isinstance(client.created_by, User)


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
