# -*- coding: utf-8 -*-
"""OAuth Token views."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required

from .models import Token

blueprint = Blueprint('oauth.token', __name__, url_prefix='/oauth/tokens',
                      static_folder='../../static')


@blueprint.route('/')
@login_required
def home():
    """Token landing page."""
    if not current_user.is_admin:
        abort(403)

    tokens = Token.query.all()

    return render_template('oauth/tokens/home.html', tokens=tokens)


@blueprint.route('/delete/<int:token_id>', methods=['GET', 'DELETE'])
@login_required
def delete(token_id):
    """Delete token."""
    if not current_user.is_admin:
        abort(403)

    token = Token.query.get(token_id)
    if not token:
        abort(404)
    else:
        token_id = token.id
        token.delete()
        flash(_('Successfully deleted OAuth2 Bearer token "%(token_id)s".', token_id=token_id),
              'success')
    return redirect(url_for('oauth.token.home'))
