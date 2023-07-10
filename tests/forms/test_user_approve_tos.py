"""Test user ApproveToSForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta

import pytest
from flask import url_for
from flask_babel import gettext as _

from xl_auth.user.forms import ApproveToSForm

from ..factories import UserFactory


@pytest.mark.usefixtures('db')
def test_validate_success():
    """Approve ToS form with success."""
    user = UserFactory(tos_approved_at=None)
    form = ApproveToSForm(user, tos_approved='y', next_redirect=url_for('user.profile'))

    assert form.validate() is True


@pytest.mark.usefixtures('db')
def test_validate_when_tos_approved_is_not_y():
    """Attempt approving ToS with 'tos_approved' set to e.g. 'no'."""
    user = UserFactory(tos_approved_at=None)
    form = ApproveToSForm(user, tos_approved='no', next_redirect=url_for('user.profile'))

    assert form.validate() is False
    assert _('Invalid option "%(value)s".', value='no') in form.tos_approved.errors


@pytest.mark.usefixtures('db')
def test_validate_when_tos_approved_at_already_set():
    """Attempt approving ToS with 'tos_approved_at' already set."""
    user = UserFactory(tos_approved_at=datetime.utcnow() - timedelta(days=20))
    form = ApproveToSForm(user, tos_approved='y', next_redirect=url_for('user.profile'))

    assert form.validate() is False
    assert _('ToS already approved at %(isoformat)s.',
             isoformat=user.tos_approved_at.isoformat() + 'Z') in form.tos_approved.errors
