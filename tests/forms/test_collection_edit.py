# -*- coding: utf-8 -*-
"""Test collection EditForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice

import pytest
from flask_babel import gettext as _
from wtforms.validators import ValidationError

from xl_auth.collection.forms import EditForm


def test_validate_without_code(superuser, collection):
    """Attempt editing entry without a code."""
    form = EditForm(superuser, collection.code, friendly_name='The old books', category='library')

    assert form.validate() is False
    assert _('This field is required.') in form.code.errors


# noinspection PyUnusedLocal
def test_validate_code_does_not_exist(superuser, db):
    """Attempt to edit entry with code that is not registered."""
    form = EditForm(superuser, 'none', code='none', friendly_name='KB wing 3', category='library')

    assert form.validate() is False
    assert _('Code does not exist') in form.code.errors


def test_validate_modifying_code(superuser, collection):
    """Attempt to edit entry with a new code."""
    form = EditForm(superuser, collection.code, code='newOne', friendly_name='KB Lib',
                    category='library')

    assert form.validate() is False
    assert _('Code cannot be modified') in form.code.errors


def test_validate_without_friendly_name(superuser, collection):
    """Attempt editing entry with friendly_name shorter than 2 chars."""
    form = EditForm(superuser, collection.code, code=collection.code, friendly_name='0',
                    category='library')

    assert form.validate() is False
    assert _('Field must be between 2 and 255 characters long.') in form.friendly_name.errors


def test_validate_unsupported_category(superuser, collection):
    """Attempt editing entry with custom/unsupported category."""
    form = EditForm(superuser, collection.code, code=collection.code, friendly_name='Secret',
                    category='Made-up by me')

    assert form.validate() is False
    assert _('Not a valid choice') in form.category.errors


def test_validate_collection_edit_as_user(user, collection):
    """Attempt to edit a collection as non-admin user."""
    form = EditForm(user, collection.code, code=collection.code,
                    friendly_name='National Library',
                    category=choice(['bibliography', 'library', 'uncategorized']))

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert e_info.value.args[0] == _('You do not have sufficient privileges for this operation.')


def test_validate_success(superuser, collection):
    """Edit entry with success."""
    form = EditForm(superuser, collection.code, code=collection.code,
                    friendly_name='National Library',
                    category=choice(['bibliography', 'library', 'uncategorized']))

    assert form.validate() is True
