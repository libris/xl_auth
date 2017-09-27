# -*- coding: utf-8 -*-
"""Test collection forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice

from flask_babel import gettext as _

from xl_auth.collection.forms import EditForm, RegisterForm


# noinspection PyUnusedLocal
def test_register_form_validate_without_code(db):
    """Attempt registering entry with empty string for code."""
    form = RegisterForm(code='', friendly_name='The old books', category='library')

    assert form.validate() is False
    assert _('This field is required.') in form.code.errors


def test_register_form_validate_with_too_long_code(db):
    """Attempt registering entry with code longer than 5 chars."""
    form = RegisterForm(code='123456', friendly_name='The hidden books', category='library')

    assert form.validate() is False
    assert _('Field must be between 1 and 5 characters long.') in form.code.errors


def test_edit_form_validate_without_code(collection):
    """Attempt editing entry without a code."""
    form = EditForm(collection.code, friendly_name='The old books', category='library')

    assert form.validate() is False
    assert _('This field is required.') in form.code.errors


def test_register_form_validate_code_already_registered(collection):
    """Attempt registering code that is already registered, irrespective of casing."""
    if collection.code.upper() != collection.code:
        existing_code_with_different_casing = collection.code.upper()
    else:
        existing_code_with_different_casing = collection.code.lower()
    assert existing_code_with_different_casing != collection.code

    form = RegisterForm(code=existing_code_with_different_casing, friendly_name='Shelf no 3',
                        category='uncategorized')

    assert form.validate() is False
    assert _('Code "%(code)s" already registered', code=collection.code) in form.code.errors


# noinspection PyUnusedLocal
def test_edit_form_validate_code_does_not_exist(db):
    """Attempt to edit entry with code that is not registered."""
    form = EditForm('none', code='none', friendly_name='KB wing 3', category='library')

    assert form.validate() is False
    assert _('Code does not exist') in form.code.errors


def test_edit_form_validate_modifying_code(collection):
    """Attempt to edit entry with a new code."""
    form = EditForm(collection.code, code='newOne', friendly_name='KB Lib', category='library')

    assert form.validate() is False
    assert _('Code cannot be modified') in form.code.errors


# noinspection PyUnusedLocal
def test_register_form_validate_without_friendly_name(db):
    """Attempt registering entry with friendly_name shorter than 2 chars."""
    form = RegisterForm(code='SFX', friendly_name='1', category='uncategorized')

    assert form.validate() is False
    assert _('Field must be between 2 and 255 characters long.') in form.friendly_name.errors


def test_edit_form_validate_without_friendly_name(collection):
    """Attempt editing entry with friendly_name shorter than 2 chars."""
    form = EditForm(collection.code, code=collection.code, friendly_name='0', category='library')

    assert form.validate() is False
    assert _('Field must be between 2 and 255 characters long.') in form.friendly_name.errors


# noinspection PyUnusedLocal
def test_register_form_validate_unsupported_category(db):
    """Attempt registering entry with custom/unsupported category."""
    form = RegisterForm(code='SF2', friendly_name='Top shelf', category='Made-up by me')

    assert form.validate() is False
    assert _('Not a valid choice') in form.category.errors


def test_edit_form_validate_unsupported_category(collection):
    """Attempt editing entry with custom/unsupported category."""
    form = EditForm(collection.code, code=collection.code, friendly_name='Secret',
                    category='Made-up by me')

    assert form.validate() is False
    assert _('Not a valid choice') in form.category.errors


def test_register_form_validate_success(collection):
    """Register entry with success (using slightly different code than already exists)."""
    slightly_different_code_than_existing_one = collection.code + 'X'
    form = RegisterForm(code=slightly_different_code_than_existing_one,
                        friendly_name='National Library, section D9, shelf 2, row 1',
                        category=choice(['bibliography', 'library', 'uncategorized']))

    assert form.validate() is True


def test_edit_form_validate_success(collection):
    """Edit entry with success."""
    form = EditForm(collection.code, code=collection.code, friendly_name='National Library',
                    category=choice(['bibliography', 'library', 'uncategorized']))

    assert form.validate() is True
