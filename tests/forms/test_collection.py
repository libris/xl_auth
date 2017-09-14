# -*- coding: utf-8 -*-
"""Test collection forms."""

from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice

from xl_auth.collection.forms import RegisterForm


# noinspection PyUnusedLocal
def test_register_form_validate_without_code(db):
    """Attempt registering with code shorter than 2 chars."""
    form = RegisterForm(code='1', friendly_name='The old books', category='library')

    assert form.validate() is False
    assert 'Field must be between 2 and 8 characters long.' in form.code.errors


def test_register_form_validate_code_already_registered(collection):
    """Enter code that is already registered."""
    form = RegisterForm(code=collection.code, friendly_name='Shelf no 3', category='uncategorized')

    assert form.validate() is False
    assert 'Code already registered' in form.code.errors


# noinspection PyUnusedLocal
def test_register_form_validate_without_friendly_name(db):
    """Attempt registering with friendly_name shorter than 2 chars."""
    form = RegisterForm(code='SFX', friendly_name='1')

    assert form.validate() is False
    assert 'Field must be between 2 and 255 characters long.' in form.friendly_name.errors


# noinspection PyUnusedLocal
def test_register_form_validate_unsupported_category(db):
    """Attempt registering with custom/unsupported category."""
    form = RegisterForm(code='SF2', friendly_name='Top shelf', category='Made-up by me')

    assert form.validate() is False
    assert "Not a valid choice" in form.category.errors


# noinspection PyUnusedLocal
def test_register_form_validate_success(db):
    """Register with success."""
    form = RegisterForm(code='XZY', friendly_name='National Library, section D9, shelf 2, row 1',
                        category=choice(['bibliography', 'library', 'uncategorized']))
    assert form.validate() is True
