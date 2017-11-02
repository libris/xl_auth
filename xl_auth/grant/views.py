# -*- coding: utf-8 -*-
"""Grant views."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required

from .models import Grant

blueprint = Blueprint('grant', __name__, url_prefix='/grants', static_folder='../static')


@blueprint.route('/')
@login_required
def home():
    """Grant landing page."""
    if not current_user.is_admin:
        abort(403)

    grants = Grant.query.all()

    return render_template('grants/home.html', grants=grants)


@blueprint.route('/delete/<int:id>', methods=['GET', 'DELETE'])
@login_required
def delete(grant_id):
    """Delete grant."""
    if not current_user.is_admin:
        abort(403)

    grant = Grant.get_by_id(grant_id)
    if not grant:
        abort(404)
    else:
        grant_id = grant.id
        grant.delete()
        flash(_('Successfully deleted OAuth2 Grant token "%(grant_id)s".', grant_id=grant_id),
              'success')
    return redirect(url_for('grant.home'))
