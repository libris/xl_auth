# -*- coding: utf-8 -*-
"""Permission views."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint

from .models import Permission

blueprint = Blueprint('Permission', __name__, url_prefix='/permissions', static_folder='../static')


@blueprint.route('/')
def home():
    """Permissions landing page."""
    permissions_list = Permission.query.all()
    return 'im a placeholder, loading {} permissions from DB'.format(len(permissions_list))
