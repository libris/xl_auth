# -*- coding: utf-8 -*-
"""Unit tests for Permission model."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt

import pytest
from sqlalchemy.exc import IntegrityError

from xl_auth.collection.models import Collection
from xl_auth.permission.models import Permission
from xl_auth.user.models import User

from ..factories import PermissionFactory


@pytest.mark.usefixtures('db')
def test_get_by_id(user, collection):
    """Get permission by ID."""
    permission = Permission(user=user, collection=collection)
    permission.save()

    retrieved = Permission.get_by_id(permission.id)
    assert retrieved == permission


@pytest.mark.usefixtures('db')
def test_created_at_defaults_to_datetime(user, collection):
    """Test creation date."""
    permission = Permission(user=user, collection=collection)
    permission.save()

    assert bool(permission.created_at)
    assert isinstance(permission.created_at, dt.datetime)


@pytest.mark.usefixtures('db')
def test_modified_at_defaults_to_current_datetime(user, collection):
    """Test modified date."""
    permission = Permission(user=user, collection=collection)
    permission.save()
    first_modified_at = permission.modified_at

    assert abs((first_modified_at - permission.created_at).total_seconds()) < 10

    permission.registrant = not permission.registrant
    permission.save()

    assert first_modified_at != permission.modified_at


@pytest.mark.usefixtures('db')
def test_factory(db):
    """Test permission factory."""
    permission = PermissionFactory()
    db.session.commit()

    assert isinstance(permission.user, User)
    assert isinstance(permission.collection, Collection)
    assert permission.registrant is False
    assert permission.cataloger is False
    assert permission.cataloging_admin is False
    assert bool(permission.modified_at)
    assert bool(permission.created_at)


@pytest.mark.usefixtures('db')
def test_repr(user, collection):
    """Check repr output."""
    permission = PermissionFactory(user=user, collection=collection)
    assert repr(permission) == '<Permission({!r}@{!r})>'.format(user, collection)


@pytest.mark.usefixtures('db')
def test_unique_constraint(user, collection):
    """Test uniqueness constraint for user-collection pairs."""
    permission = PermissionFactory(user=user, collection=collection)
    permission.save()

    duplicate_permission = PermissionFactory(user=user, collection=collection)
    # noinspection PyUnusedLocal
    with pytest.raises(IntegrityError) as e_info:  # noqa
        duplicate_permission.save()
