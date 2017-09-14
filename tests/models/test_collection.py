# -*- coding: utf-8 -*-
"""Unit tests for Collection model."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt

import pytest
from six import string_types

from xl_auth.collection.models import Collection

from ..factories import CollectionFactory


@pytest.mark.usefixtures('db')
def test_get_by_id():
    """Get collection by ID."""
    collection = Collection(code='SKB', friendly_name='Literature by Strindberg')
    collection.save()

    retrieved = Collection.get_by_id(collection.id)
    assert retrieved == collection


@pytest.mark.usefixtures('db')
def test_created_at_defaults_to_datetime():
    """Test creation date."""
    collection = Collection('KBX', 'Secret books')
    collection.save()
    assert bool(collection.created_at)
    assert isinstance(collection.created_at, dt.datetime)


@pytest.mark.usefixtures('db')
def test_category_is_nullable():
    """Test null category."""
    collection = Collection('KBY', 'Old books', category=None)
    collection.save()
    assert collection.category is None


@pytest.mark.usefixtures('db')
def test_factory(db):
    """Test collection factory."""
    collection = CollectionFactory()
    db.session.commit()
    assert bool(collection.code)
    assert bool(collection.friendly_name)
    assert isinstance(collection.category, string_types) or collection.category is None
    assert bool(collection.created_at)
    assert collection.active is True


@pytest.mark.usefixtures('db')
def test_repr():
    """Check repr output."""
    collection = CollectionFactory(code='KBZ')
    assert repr(collection) == '<Collection({!r})>'.format('KBZ')
