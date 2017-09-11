# -*- coding: utf-8 -*-
"""Unit tests for User model."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt

import pytest

from xl_auth.user.models import Role, User

from ..factories import UserFactory


@pytest.mark.usefixtures('db')
def test_get_by_id():
    """Get user by ID."""
    user = User('foo', 'foo@bar.com')
    user.save()

    retrieved = User.get_by_id(user.id)
    assert retrieved == user


@pytest.mark.usefixtures('db')
def test_created_at_defaults_to_datetime():
    """Test creation date."""
    user = User(username='foo', email='foo@bar.com')
    user.save()
    assert bool(user.created_at)
    assert isinstance(user.created_at, dt.datetime)


@pytest.mark.usefixtures('db')
def test_password_is_nullable():
    """Test null password."""
    user = User(username='foo', email='foo@bar.com')
    user.save()
    assert user.password is None


@pytest.mark.usefixtures('db')
def test_factory(db):
    """Test user factory."""
    user = UserFactory(password='myPrecious')
    db.session.commit()
    assert bool(user.username)
    assert bool(user.email)
    assert bool(user.created_at)
    assert user.is_admin is False
    assert user.active is True
    assert user.check_password('myPrecious')


@pytest.mark.usefixtures('db')
def test_check_password():
    """Check password."""
    user = User.create(username='foo', email='foo@bar.com',
                       password='fooBarBaz123')
    assert user.check_password('fooBarBaz123') is True
    assert user.check_password('barFooBaz') is False


@pytest.mark.usefixtures('db')
def test_full_name():
    """User full name."""
    user = UserFactory(first_name='Foo', last_name='Bar')
    assert user.full_name == 'Foo Bar'


@pytest.mark.usefixtures('db')
def test_roles():
    """Add a role to a user."""
    role = Role(name='admin')
    role.save()
    user = UserFactory()
    user.roles.append(role)
    user.save()
    assert role in user.roles