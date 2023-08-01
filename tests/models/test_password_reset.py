"""Unit tests for PasswordReset model."""


import datetime as dt

import pytest
from six import string_types
from sqlalchemy.exc import IntegrityError

from xl_auth.user.models import PasswordReset, User

from ..factories import PasswordResetFactory, UserFactory


def test_get_by_id(user):
    """Get password reset by ID."""
    password_reset = PasswordReset(user)
    password_reset.save()

    retrieved = PasswordReset.get_by_id(password_reset.id)
    assert retrieved == password_reset


def test_created_at_defaults_to_datetime(user):
    """Test creation date."""
    password_reset = PasswordReset(user)
    password_reset.save()
    assert bool(password_reset.created_at)
    assert isinstance(password_reset.created_at, dt.datetime)


def test_modified_at_defaults_to_current_datetime(user):
    """Test modified date."""
    password_reset = PasswordReset(user)
    password_reset.save()
    first_modified_at = password_reset.modified_at

    assert abs((first_modified_at - password_reset.created_at).total_seconds()) < 10

    password_reset.is_active = not password_reset.is_active
    password_reset.save()

    # Initial 'modified_at' has been overwritten.
    assert first_modified_at != password_reset.modified_at


def test_code_defaults_to_a_random_one_with_length_32(user):
    """Test code field is automatically assigned some 32-char random string."""
    password_reset_1 = PasswordReset(user)
    password_reset_1.save()
    assert password_reset_1.code is not None
    assert len(password_reset_1.code) == 32

    password_reset_2 = PasswordReset(user)
    password_reset_2.save()
    assert password_reset_2.code != password_reset_1.code
    assert len(password_reset_2.code) == 32


def test_factory(db):
    """Test password reset factory."""
    password_reset = PasswordResetFactory()
    db.session.commit()
    assert isinstance(password_reset.user, User)
    assert isinstance(password_reset.code, string_types)
    assert isinstance(password_reset.is_active, bool)
    assert isinstance(password_reset.expires_at, dt.datetime)
    assert isinstance(password_reset.modified_at, dt.datetime)
    assert isinstance(password_reset.created_at, dt.datetime)


@pytest.mark.usefixtures('db')
def test_get_by_email_and_code():
    """Check get_by_email_and_code."""
    password_reset = PasswordReset.create(user=UserFactory())
    assert PasswordReset.get_by_email_and_code(password_reset.user.email.upper(),
                                               password_reset.code) == password_reset
    assert PasswordReset.get_by_email_and_code(password_reset.user.email, '89ab' * 8) is None


@pytest.mark.usefixtures('db')
def test_repr():
    """Check repr output."""
    password_reset = PasswordResetFactory(user=UserFactory(email='foo@example.com'))
    assert repr(password_reset) == '<PasswordReset({!r})>'.format(password_reset.user.email)


def test_unique_constraint(user):
    """Test uniqueness constraint for user-code pairs."""
    password_reset = PasswordResetFactory(user=user)
    password_reset.save()

    duplicate_password_reset = PasswordResetFactory(user=user)
    duplicate_password_reset.code = password_reset.code
    # noinspection PyUnusedLocal
    with pytest.raises(IntegrityError) as e_info:  # noqa
        duplicate_password_reset.save()
