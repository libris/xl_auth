# -*- coding: utf-8 -*-
"""Collection views."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from ..utils import flash_errors
from .forms import EditForm, RegisterForm
from .models import Collection

blueprint = Blueprint('collection', __name__, url_prefix='/collections', static_folder='../static')


@blueprint.route('/')
@login_required
def home():
    """Collections landing page."""
    collections_list_active = Collection.query.filter_by(is_active=True).order_by('code')
    collections_list_inactive = Collection.query.filter_by(is_active=False).order_by('code')

    return render_template('collections/home.html', collections_list_active=collections_list_active,
                           collections_list_inactive=collections_list_inactive)


@blueprint.route('/register/', methods=['GET', 'POST'])
@login_required
def register():
    """Register new collection."""
    if not current_user.is_admin:
        abort(403)

    register_collection_form = RegisterForm(current_user, request.form)
    if register_collection_form.validate_on_submit():
        Collection.create_as(current_user,
                             code=register_collection_form.code.data,
                             friendly_name=register_collection_form.friendly_name.data,
                             category=register_collection_form.category.data,
                             is_active=True)
        flash(_('Thank you for registering a new collection.'), 'success')
        return redirect(url_for('collection.home'))
    else:
        flash_errors(register_collection_form)
    return render_template('collections/register.html',
                           register_collection_form=register_collection_form)


@blueprint.route('/edit/<string:collection_code>', methods=['GET', 'POST'])
@login_required
def edit(collection_code):
    """Edit existing collection."""
    if not current_user.is_admin:
        abort(403)

    collection = Collection.query.filter(Collection.code == collection_code).first()
    if not collection:
        flash(_('Collection code "%(code)s" does not exist', code=collection_code), 'danger')
        return redirect(url_for('collection.home'))

    edit_collection_form = EditForm(current_user, collection_code, request.form)
    if edit_collection_form.validate_on_submit():
        collection.update_as(current_user,
                             friendly_name=edit_collection_form.friendly_name.data,
                             category=edit_collection_form.category.data).save()
        flash(_('Thank you for editing collection "%(code)s".', code=collection.code), 'success')
        return redirect(url_for('collection.home'))
    else:
        flash_errors(edit_collection_form)
    return render_template('collections/edit.html', edit_collection_form=edit_collection_form,
                           collection=collection)
