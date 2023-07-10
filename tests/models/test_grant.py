"""Unit tests for Grant model."""


import pytest

from xl_auth.oauth.grant.models import Grant

from ..factories import GrantFactory


def test_get_by_id(user, client):
    """Get grant by ID."""
    grant = Grant(user=user, client=client, code='temp-secret', redirect_uri='http://example.com',
                  scopes='read write')
    grant.save()

    retrieved = grant.get_by_id(grant.id)
    assert retrieved == grant


def test_factory(db):
    """Test grant factory."""
    grant = GrantFactory()
    db.session.commit()
    assert bool(grant.user_id)
    assert bool(grant.client_id)
    assert bool(grant.code)
    assert bool(grant.redirect_uri)
    assert bool(grant.expires_at)
    assert bool(grant.scopes)
    assert grant.scopes == ['read', 'write']


def test_get_all_by_user(db, user, client):
    """Get all grants issued for a specific user."""
    grant = Grant(user=user, client=client, code='temp-secret', redirect_uri='http://example.com',
                  scopes='read write')
    grant.save()
    other_grant = GrantFactory()
    db.session.commit()

    grants = Grant.get_all_by_user(user)
    assert other_grant not in grants
    assert [grant] == grants


def test_delete_all_by_user(db, user, client):
    """Delete all grants issued for a specific user."""
    grant = Grant(user=user, client=client, code='temp-secret', redirect_uri='http://example.com',
                  scopes='read write')
    grant.save()
    other_grant = GrantFactory()
    db.session.commit()

    Grant.delete_all_by_user(user)
    db.session.commit()
    grants = Grant.query.all()
    assert grant not in grants
    assert [other_grant] == grants


@pytest.mark.usefixtures('db')
def test_scopes():
    """Test scopes."""
    grant = GrantFactory(scopes='readWrite readOnly')
    assert grant.scopes == ['readWrite', 'readOnly']

    grant.scopes = ['read', 'write']
    assert grant.scopes == ['read', 'write']


@pytest.mark.usefixtures('db')
def test_repr():
    """Check repr output."""
    grant = GrantFactory()
    assert repr(grant) == '<Grant({!r},{!r})>'.format(grant.user.email, grant.client.name)
