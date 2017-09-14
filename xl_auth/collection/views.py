# -*- coding: utf-8 -*-
"""Collection views."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, flash, render_template, request, redirect, url_for

from ..utils import flash_errors

from .forms import RegisterForm
from .models import Collection

blueprint = Blueprint('collection', __name__, url_prefix='/collections', static_folder='../static')


@blueprint.route('/')
def home():
    """Collections landing page."""
    collections_list = Collection.query.all()
    return render_template('collection/home.html', collections_list=collections_list)


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new collection."""
    register_collection_form = RegisterForm(request.form)
    if register_collection_form.validate_on_submit():
        Collection.create(code=register_collection_form.code.data,
                          friendly_name=register_collection_form.friendly_name.data,
                          category=register_collection_form.category.data,
                          active=True)
        flash('Thank you for registering a new collection.', 'success')
        return redirect(url_for('collection.home'))
    else:
        flash_errors(register_collection_form)
    return render_template('collection/register.html',
                           register_collection_form=register_collection_form)
