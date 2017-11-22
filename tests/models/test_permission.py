# -*- coding: utf-8 -*-
"""Unit tests for Permission model."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from xl_auth.collection.models import Collection
from xl_auth.permission.models import Permission
from xl_auth.user.models import User

from ..factories import PermissionFactory, SuperUserFactory


def test_get_by_id(superuser, user, collection):
    """Get permission by ID."""
    permission = Permission(user=user, collection=collection)
    permission.save_as(superuser)

    retrieved = Permission.get_by_id(permission.id)
    assert retrieved == permission


def test_created_by_and_modified_by_is_updated(superuser, user, collection):
    """Test created/modified by."""
    permission = Permission(user=user, collection=collection)
    permission.save_as(superuser)
    assert permission.created_by_id == superuser.id
    assert permission.created_by == superuser
    assert permission.modified_by_id == superuser.id
    assert permission.modified_by == superuser

    # Another superuser updates something in the permission.
    another_superuser = SuperUserFactory()
    permission.update_as(another_superuser, commit=True, cataloger=not permission.cataloger)
    assert permission.created_by == superuser
    assert permission.modified_by == another_superuser


def test_created_at_defaults_to_datetime(superuser, user, collection):
    """Test creation date."""
    permission = Permission(user=user, collection=collection)
    permission.save_as(superuser)

    assert bool(permission.created_at)
    assert isinstance(permission.created_at, datetime)


def test_modified_at_defaults_to_current_datetime(superuser, user, collection):
    """Test modified date."""
    permission = Permission(user=user, collection=collection)
    permission.save_as(superuser)
    first_modified_at = permission.modified_at

    assert abs((first_modified_at - permission.created_at).total_seconds()) < 10

    permission.registrant = not permission.registrant
    permission.save()

    assert first_modified_at != permission.modified_at


def test_factory(db):
    """Test permission factory."""
    permission = PermissionFactory()
    db.session.commit()

    assert isinstance(permission.user, User)
    assert isinstance(permission.collection, Collection)

    assert permission.registrant is False
    assert permission.cataloger is False
    assert permission.cataloging_admin is False

    assert isinstance(permission.modified_at, datetime)
    assert isinstance(permission.modified_by, User)
    assert isinstance(permission.created_at, datetime)
    assert isinstance(permission.created_by, User)


def test_repr(user, collection):
    """Check repr output."""
    permission = PermissionFactory(user=user, collection=collection)
    assert repr(permission) == '<Permission({!r}@{!r})>'.format(user, collection)


def test_unique_constraint(user, collection):
    """Test uniqueness constraint for user-collection pairs."""
    permission = PermissionFactory(user=user, collection=collection)
    permission.save()

    duplicate_permission = PermissionFactory(user=user, collection=collection)
    # noinspection PyUnusedLocal
    with pytest.raises(IntegrityError) as e_info:  # noqa
        duplicate_permission.save()
