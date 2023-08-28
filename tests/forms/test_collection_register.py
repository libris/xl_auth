"""Test collection RegisterForm."""


from random import choice

import pytest
from flask_babel import gettext as _
from wtforms.validators import ValidationError

from xl_auth.collection.forms import RegisterForm


# noinspection PyUnusedLocal
def test_validate_without_code(superuser, db):
    """Attempt registering entry with empty string for code."""
    form = RegisterForm(superuser, code='', friendly_name='The old books', category='library')

    assert form.validate() is False
    assert _('This field is required.') in form.code.errors


def test_validate_with_too_long_code(superuser, db):
    """Attempt registering entry with code longer than 5 chars."""
    form = RegisterForm(superuser, code='123456', friendly_name='The hidden books',
                        category='library')

    assert form.validate() is False
    assert _('Field must be between 1 and 5 characters long.') in form.code.errors


def test_validate_code_already_registered(superuser, collection):
    """Attempt registering code that is already registered."""
    form = RegisterForm(superuser, code=collection.code, friendly_name='Shelf no 3',
                        category='uncategorized')

    assert form.validate() is False
    assert _('Code "%(code)s" already registered', code=collection.code) in form.code.errors


def test_validate_code_already_registered_with_different_casing(superuser, collection):
    """Attempt registering code that is already registered, this time with different casing."""
    collection.code = 'UPPER'
    collection.save()
    form = RegisterForm(superuser, code=collection.code.lower(), friendly_name='Uppsala',
                        category='library')

    assert form.validate() is False
    assert _('Code "%(code)s" already registered', code=collection.code) in form.code.errors


# noinspection PyUnusedLocal
def test_validate_without_friendly_name(superuser, db):
    """Attempt registering entry with friendly_name shorter than 2 chars."""
    form = RegisterForm(superuser, code='SFX', friendly_name='1', category='uncategorized')

    assert form.validate() is False
    assert _('Field must be between 2 and 255 characters long.') in form.friendly_name.errors


# noinspection PyUnusedLocal
def test_validate_unsupported_category(superuser, db):
    """Attempt registering entry with custom/unsupported category."""
    form = RegisterForm(superuser, code='SF2', friendly_name='Top shelf', category='Made-up by me')

    assert form.validate() is False
    assert _('Not a valid choice') in form.category.errors


def test_user_cannot_register_collection(user):
    """Attempt to register a collection as regular user."""
    form = RegisterForm(user, code='ABCDE',
                        friendly_name='National Library, section D9, shelf 2, row 1',
                        category=choice(['bibliography', 'library', 'uncategorized']))

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert e_info.value.args[0] == _('You do not have sufficient privileges for this operation.')


def test_validate_success(superuser, collection):
    """Register entry with success (using slightly different code than already exists)."""
    slightly_different_code_than_existing_one = collection.code + 'X'
    form = RegisterForm(superuser, code=slightly_different_code_than_existing_one,
                        friendly_name='National Library, section D9, shelf 2, row 1',
                        category=choice(['bibliography', 'library', 'uncategorized']))

    assert form.validate() is True
