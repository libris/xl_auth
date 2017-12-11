# -*- coding: utf-8 -*-
"""Unit tests for User model."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

import pytest
from flask_babel import gettext as _

from xl_auth.permission.models import Permission
from xl_auth.user.models import PasswordReset, Role, User

from ..factories import CollectionFactory, PermissionFactory, UserFactory


def test_get_by_id(superuser):
    """Get user by ID."""
    user = User('foo@bar.com', 'Foo Bar')
    user.save_as(superuser)

    retrieved = User.get_by_id(user.id)
    assert retrieved == user


def test_created_by_and_modified_by_is_updated(superuser):
    """Test created/modified by."""
    user = User(email='foo@bar.com', full_name='Foo Bar')
    user.save_as(superuser)
    assert user.created_by_id == superuser.id
    assert user.created_by == superuser
    assert user.modified_by_id == superuser.id
    assert user.modified_by == superuser

    # User updates something in their profile.
    user.update_as(user, commit=True, full_name='Bar Foo')
    assert user.created_by == superuser
    assert user.modified_by == user


def test_created_at_defaults_to_datetime(superuser):
    """Test creation date."""
    user = User(email='foo@bar.com', full_name='Foo Bar')
    user.save_as(superuser)
    assert bool(user.created_at)
    assert isinstance(user.created_at, datetime)


def test_modified_at_defaults_to_current_datetime(superuser):
    """Test modified date."""
    user = User('foo@kb.se', 'Wrong Name')
    user.save_as(superuser)
    first_modified_at = user.modified_at

    assert abs((first_modified_at - user.created_at).total_seconds()) < 10

    user.full_name = 'Correct Name'
    user.save_as(user)

    # Initial 'modified_at' has been overwritten.
    assert first_modified_at != user.modified_at


def test_update_last_login_does_not_update_modified_at(superuser):
    """Test modified date."""
    user = User('foo@kb.se', 'Hello World')
    user.save_as(superuser)
    first_modified_at = user.modified_at

    # Update 'last_login_at' timestamp.
    user.update_last_login(commit=True)

    # Initial 'modified_at' is still the same.
    assert first_modified_at == user.modified_at


def test_tos_approved_at_defaults_to_null(superuser):
    """Test Terms of Service datetime field is not populated automatically."""
    user = User(email='foo@bar.com', full_name='Foo Bar')
    user.save_as(superuser)
    assert user.tos_approved_at is None


def test_password_defaults_to_a_random_one(superuser):
    """Test empty password field is assigned some random password, instead of being set to null."""
    user = User(email='foo@bar.com', full_name='Foo Bar')
    user.save_as(superuser)
    assert user.password is not None


@pytest.mark.usefixtures('db')
def test_factory(db):
    """Test user factory."""
    user = UserFactory(password='myPrecious')
    db.session.commit()

    assert bool(user.email)
    assert bool(user.full_name)
    assert user.check_password('myPrecious')
    assert user.last_login_at is None
    assert user.is_active is True
    assert user.is_admin is False

    assert isinstance(user.tos_approved_at, datetime)

    assert isinstance(user.permissions, list)
    assert isinstance(user.roles, list)
    assert isinstance(user.password_resets, list)

    assert isinstance(user.modified_at, datetime)
    assert isinstance(user.modified_by, User)
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.created_by, User)


def test_check_password(superuser):
    """Check password."""
    user = User.create_as(superuser, email='foo@bar.com', full_name='Foo Bar',
                          password='fooBarBaz123')
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
    permission.save_as(user)

    assert permission in user.permissions


@pytest.mark.usefixtures('db')
def test_removing_permissions(collection):
    """Withdraw permission from a user."""
    user = UserFactory()
    user.save()
    permission = Permission(user=user, collection=collection)
    permission.save_as(user)
    permission.delete()

    assert permission not in user.permissions


def test_is_cataloging_admin(superuser, user):
    """Test is_cataloging_admin return value."""
    collection1, collection2 = CollectionFactory(), CollectionFactory()
    not_admin_permission = Permission(user=user, collection=collection1,
                                      cataloging_admin=False).save_as(superuser)
    admin_permission = Permission(user=user, collection=collection2,
                                  cataloging_admin=True).save_as(superuser)

    assert not_admin_permission in user.permissions and admin_permission in user.permissions
    assert user.is_cataloging_admin is True

    admin_permission.delete()
    assert admin_permission not in user.permissions
    assert user.is_cataloging_admin is False

    not_admin_permission.delete()
    assert user.permissions == []
    assert user.is_cataloging_admin is False


def test_is_cataloging_admin_for(user, collection, superuser):
    """Test is_cataloging_admin_for return value."""
    other_collection = CollectionFactory()
    not_admin_permission = Permission(user=user, collection=collection,
                                      cataloging_admin=False).save_as(superuser)
    admin_permission = Permission(user=user, collection=other_collection,
                                  cataloging_admin=True).save_as(superuser)

    assert user.is_cataloging_admin_for(not_admin_permission.collection) is False
    assert user.is_cataloging_admin_for(admin_permission.collection) is True


def test_has_any_permission_for(user, collection, superuser):
    """Test has_any_permission_for return value."""
    other_collection = CollectionFactory()
    regular_permission = Permission(user=user, collection=other_collection,
                                    cataloging_admin=False).save_as(superuser)
    assert user.has_any_permission_for(collection) is False
    regular_permission.collection = collection
    regular_permission.save()
    assert user.has_any_permission_for(collection) is True


def test_get_permissions_as_seen_by_self(user):
    """Test getting permissions for self."""
    non_admin_permission = PermissionFactory(user=user, cataloging_admin=False).save_as(user)
    assert user.get_permissions_as_seen_by(user) == [non_admin_permission]
    admin_permission = PermissionFactory(user=user, cataloging_admin=True).save_as(user)

    seen_permissions = user.get_permissions_as_seen_by(user)
    assert len(seen_permissions) == 2
    assert non_admin_permission in seen_permissions
    assert admin_permission in seen_permissions


def test_get_permissions_as_seen_by_other_user(user, superuser):
    """Test getting permissions for someone as regular user."""
    collection1, collection2 = CollectionFactory(), CollectionFactory()
    Permission(user=superuser, collection=collection1, cataloging_admin=True).save_as(superuser)
    col2_permission = Permission(user=superuser, collection=collection2,
                                 cataloging_admin=False).save_as(superuser)

    # If we have no permissions, we see no permissions
    assert superuser.get_permissions_as_seen_by(user) == []

    # If we only have non-cataloging admin permissions, we see no permissions
    Permission(user=user, collection=collection1, cataloging_admin=False).save_as(superuser)
    assert superuser.get_permissions_as_seen_by(user) == []

    # If we have cataloging admin permissions, we see permissions for that collection
    Permission(user=user, collection=collection2, cataloging_admin=True).save_as(superuser)
    assert superuser.get_permissions_as_seen_by(user) == [col2_permission]


def test_get_permissions_as_seen_by_superuser(user, superuser):
    """Test getting permissions for someone as superuser."""
    non_admin_permission = PermissionFactory(user=user, cataloging_admin=False).save_as(user)
    assert user.get_permissions_as_seen_by(user) == [non_admin_permission]
    admin_permission = PermissionFactory(user=user, cataloging_admin=True).save_as(user)

    # Same as for regular user looking at their own permissions
    seen_permissions = user.get_permissions_as_seen_by(superuser)
    assert len(seen_permissions) == 2
    assert non_admin_permission in seen_permissions
    assert admin_permission in seen_permissions


def test_get_cataloging_admin_permissions(user):
    """Test getting all cataloging admin permissions."""
    assert user.get_cataloging_admin_permissions() == []

    PermissionFactory(user=user, cataloging_admin=False).save_as(user)
    assert user.get_cataloging_admin_permissions() == []

    admin_permission = PermissionFactory(user=user, cataloging_admin=True).save_as(user)
    assert user.get_cataloging_admin_permissions() == [admin_permission]


def test_get_permissions_label_help_text(user, superuser):
    """Test getting permissions label help text."""
    assert superuser.get_permissions_label_help_text_as_seen_by(user) == ''
    PermissionFactory(user=user, cataloging_admin=True).save_as(user)
    assert (superuser.get_permissions_label_help_text_as_seen_by(user) ==
            _('You will only see permissions for those collections that you are '
              'cataloging admin for.'))


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
def test_adding_password_reset():
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
def test_removing_password_reset():
    """Remove password reset from a user."""
    user = UserFactory()
    user.save()
    password_reset = PasswordReset(user)
    password_reset.save()
    password_reset.delete()

    assert password_reset not in user.password_resets
