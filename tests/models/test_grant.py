# -*- coding: utf-8 -*-
"""Unit tests for Grant model."""

from __future__ import absolute_import, division, print_function, unicode_literals

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
