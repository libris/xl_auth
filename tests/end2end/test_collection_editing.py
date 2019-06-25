# -*- coding: utf-8 -*-
"""Test editing existing collections."""

from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice

from flask import url_for
from flask_babel import gettext as _
from jinja2 import escape

from xl_auth.collection.models import Collection


def test_superuser_can_edit_existing_collection(superuser, collection, testapp):
    """Edit an existing collection."""
    # Check expected premises
    collection_creator = collection.created_by
    initial_modified_by = collection.modified_by
    assert collection_creator != superuser and initial_modified_by != superuser
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Clicks Collections button
    res = res.click(href=url_for('collection.home'), index=0)
    # Clicks Edit button
    res = res.click(href='/collections/edit/' + collection.code)
    # Fills out the form
    form = res.forms['editCollectionForm']
    form['code'] = collection.code
    form['friendly_name'] = 'New friendly-name for {}'.format(collection.code)
    form['category'] = choice(list(
        {'uncategorized', 'bibliography', 'library'} - {collection.category}))
    form['is_super'] = not collection.is_super
    # Submits
    res = form.submit().follow()
    assert res.status_code == 200
    # The collection was edited
    edited_collection = Collection.query.filter(Collection.code == collection.code).first()
    assert edited_collection.friendly_name == form['friendly_name'].value
    assert edited_collection.category == form['category'].value
    assert edited_collection.is_super == form['is_super'].checked
    # 'modified_by' is updated to reflect change, with 'created_by' intact
    assert edited_collection.created_by == collection_creator
    assert edited_collection.modified_by == superuser
    # The edited collection is listed under existing collections
    collection_id = 'collection-{0}'.format(form['code'].value)
    collection_anchor_xpath = "//a[@class='anchor' and @id='{0}']".format(collection_id)
    assert len(res.lxml.xpath(collection_anchor_xpath)) == 1

    # Two elements, because we have both the anchor and the actual text
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(form['code'].value))) == 2
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(form['friendly_name'].value))) == 1

    if form['category'].value in {'bibliography', 'library'}:
        assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(
            _(form['category'].value.capitalize())))) == 1
    else:
        assert len(res.lxml.xpath("//td[contains(., '{0}')]/ancestor::tr/td[contains(., '{1}')]"
                                  .format(form['code'].value, _('No category')))) == 1


def test_superuser_sees_error_message_if_code_is_changed(superuser, collection, testapp):
    """Show error if form modifies collection code."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Goes to edit page for existing collection.
    res = testapp.get(url_for('collection.edit', collection_code=collection.code))
    # Fills out form, and changes code.
    form = res.forms['editCollectionForm']
    form['code'] = 'newOne'
    form['friendly_name'] = collection.friendly_name
    form['category'] = collection.category
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Code'), _('Code cannot be modified')) in res


def test_superuser_sees_error_message_if_friendly_name_is_missing(superuser, collection, testapp):
    """Show error if form does not include Name."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Goes to edit page for existing collection.
    res = testapp.get(url_for('collection.edit', collection_code=collection.code))
    # Fills out form, but omits friendly_name.
    form = res.forms['editCollectionForm']
    form['friendly_name'] = ''
    form['category'] = choice(['uncategorized', 'bibliography', 'library'])
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Name'), _('This field is required.')) in res


def test_superuser_sees_error_message_if_category_is_missing(superuser, collection, testapp):
    """Show error if form does not include a valid category."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Goes to edit page for existing collection.
    res = testapp.get(url_for('collection.edit', collection_code=collection.code))
    # Fills out form, but omits category.
    form = res.forms['editCollectionForm']
    form['friendly_name'] = 'Important books'
    form['category'].force_value('')
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Category'), _('Not a valid choice')) in res


def test_superuser_sees_error_message_if_collection_does_not_exist(superuser, collection, testapp):
    """Show error if collection already registered."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Goes to edit page for existing collection.
    res = testapp.get(url_for('collection.edit', collection_code='notFound')).follow()
    # Sees error message.
    assert escape(_('Collection code "%(code)s" does not exist', code='notFound')) in res


def test_user_cannot_edit_collection(user, collection, testapp):
    """Attempt to edit a collection."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # We click the Collections button
    res = res.click(href=url_for('collection.home'), index=0)

    # No Edit buttons for regular users
    assert res.lxml.xpath("//a[contains(@text,'{0}')]".format(_('Edit'))) == []

    # Try to go directly to edit
    testapp.get('/collections/edit/1', status=403)
