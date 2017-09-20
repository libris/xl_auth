# -*- coding: utf-8 -*-
"""User views."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, render_template
from flask_login import login_required

blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')


@blueprint.route('/')
@login_required
def members():
    """List members."""
    return render_template('users/home.html')
