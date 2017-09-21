# -*- coding: utf-8 -*-
"""Collection views."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _

from ..utils import flash_errors
from .forms import EditForm, RegisterForm
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
        flash(_('Thank you for registering a new collection.'), 'success')
        return redirect(url_for('collection.home'))
    else:
        flash_errors(register_collection_form)
    return render_template('collection/register.html',
                           register_collection_form=register_collection_form)


@blueprint.route('/edit/<string:collection_code>', methods=['GET', 'POST'])
def edit(collection_code):
    """Edit existing collection."""
    collection = Collection.query.filter(Collection.code == collection_code).first()
    if not collection:
        flash(_('Collection code "%(code)s" does not exist', code=collection_code), 'danger')
        return redirect(url_for('collection.home'))

    edit_collection_form = EditForm(collection_code, request.form)
    if edit_collection_form.validate_on_submit():
        collection.update(friendly_name=edit_collection_form.friendly_name.data,
                          category=edit_collection_form.category.data).save()
        flash(_('Thank you for editing collection "%(code)s".', code=collection.code), 'success')
        return redirect(url_for('collection.home'))
    else:
        flash_errors(edit_collection_form)
    return render_template('collection/edit.html', edit_collection_form=edit_collection_form,
                           collection=collection)
