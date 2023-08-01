"""Test user EditDetailsForm."""


import pytest
from flask_babel import gettext as _
from wtforms.validators import ValidationError

from xl_auth.user.forms import EditDetailsForm


def test_user_can_edit_self(user):
    """Edit own full_name with success."""
    form = EditDetailsForm(user, user.email, username=user.email, full_name='New Name')

    assert form.validate() is True


def test_user_cannot_edit_username(user):
    """Attempt to edit username."""
    form = EditDetailsForm(user, user.email, username='other@example.com', full_name=user.full_name)

    assert form.validate() is False
    assert _('Email cannot be modified') in form.username.errors


def test_user_cannot_edit_other(superuser, user):
    """Attempt to edit another user's details."""
    form = EditDetailsForm(user, superuser.email, username=superuser.email, full_name='New Name')

    with pytest.raises(ValidationError) as e_info:
        form.validate()
    assert e_info.value.args[0] == _('You do not have sufficient privileges for this operation.')
