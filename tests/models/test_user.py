# -*- coding: utf-8 -*-
"""Unit tests for User model."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt

import pytest

from xl_auth.permission.models import Permission
from xl_auth.user.models import PasswordReset, Role, User

from ..factories import UserFactory


@pytest.mark.usefixtures('db')
def test_get_by_id():
    """Get user by ID."""
    user = User('foo@bar.com', 'Mr. Foo Bar')
    user.save()

    retrieved = User.get_by_id(user.id)
    assert retrieved == user


@pytest.mark.usefixtures('db')
def test_created_at_defaults_to_datetime():
    """Test creation date."""
    user = User(email='foo@bar.com', full_name='Mr. Foo Bar')
    user.save()
    assert bool(user.created_at)
    assert isinstance(user.created_at, dt.datetime)


@pytest.mark.usefixtures('db')
def test_modified_at_defaults_to_current_datetime():
    """Test modified date."""
    user = User('foo@kb.se', 'Wrong Name')
    user.save()
    first_modified_at = user.modified_at

    assert abs((first_modified_at - user.created_at).total_seconds()) < 10

    user.full_name = 'Correct Name'
    user.save()

    # Initial 'modified_at' has been overwritten.
    assert first_modified_at != user.modified_at


@pytest.mark.usefixtures('db')
def test_update_last_login_does_not_update_modified_at():
    """Test modified date."""
    user = User('foo@kb.se', 'Hello World')
    user.save()
    first_modified_at = user.modified_at

    # Update 'last_login_at' timestamp.
    user.update_last_login(commit=True)

    # Initial 'modified_at' is still the same.
    assert first_modified_at == user.modified_at


@pytest.mark.usefixtures('db')
def test_password_defaults_to_a_random_one():
    """Test empty password field is assigned some random password, instead of being set to tull."""
    user = User(email='foo@bar.com', full_name='Mr. Foo Bar')
    user.save()
    assert user.password is not None


@pytest.mark.usefixtures('db')
def test_factory(db):
    """Test user factory."""
    user = UserFactory(password='myPrecious')
    db.session.commit()
    assert bool(user.email)
    assert bool(user.full_name)
    assert bool(user.modified_at)
    assert bool(user.created_at)
    assert isinstance(user.permissions, list)
    assert isinstance(user.roles, list)
    assert user.is_admin is False
    assert user.is_active is True
    assert user.check_password('myPrecious')
    assert user.last_login_at is None


@pytest.mark.usefixtures('db')
def test_check_password():
    """Check password."""
    user = User.create(None, email='foo@bar.com', full_name='Mr. Foo Bar', password='fooBarBaz123')
    assert user.check_password('fooBarBaz123') is True
    assert user.check_password('barFooBaz') is False


@pytest.mark.usefixtures('db')
def test_full_name():
    """User full name."""
    user = UserFactory(full_name='Foo Bar')
    assert user.full_name == 'Foo Bar'


@pytest.mark.usefixtures('db')
def test_adding_permissions(collection):
    """Grant a permission to a user."""
    user = UserFactory()
    user.save()
    permission = Permission(user=user, collection=collection)
    permission.save()

    assert permission in user.permissions


@pytest.mark.usefixtures('db')
def test_removing_permissions(collection):
    """Withdraw permission from a user."""
    user = UserFactory()
    user.save()
    permission = Permission(user=user, collection=collection)
    permission.save()
    permission.delete()

    assert permission not in user.permissions


@pytest.mark.usefixtures('db')
def test_get_gravatar_url():
    """Check get_gravatar_url output."""
    user = UserFactory(email='foo@example.com')

    assert user.get_gravatar_url(64) == 'https://www.gravatar.com/avatar/' \
                                        'b48def645758b95537d4424c84d1a9ff?d=mm&s=64'


@pytest.mark.usefixtures('db')
def test_repr():
    """Check repr output."""
    user = UserFactory(email='foo@example.com')
    assert repr(user) == '<User({!r})>'.format(user.email)


@pytest.mark.usefixtures('db')
def test_roles():
    """Add a role to a user."""
    role = Role(name='admin')
    role.save()
    assert repr(role) == '<Role({})>'.format(role.name)
    user = UserFactory()
    user.roles.append(role)
    user.save()
    assert role in user.roles


@pytest.mark.usefixtures('db')
def test_adding_password_reset(collection):
    """Associate user with a password reset code."""
    user = UserFactory()
    user.save()
    password_reset = PasswordReset(user, is_active=False)
    password_reset.save()

    assert password_reset in user.password_resets

    other_password_reset = PasswordReset(user)
    other_password_reset.save()
    assert other_password_reset in user.password_resets

    assert user.password_resets == [password_reset, other_password_reset]


@pytest.mark.usefixtures('db')
def test_removing_password_reset(collection):
    """Remove password reset from a user."""
    user = UserFactory()
    user.save()
    password_reset = PasswordReset(user)
    password_reset.save()
    password_reset.delete()

    assert password_reset not in user.password_resets
