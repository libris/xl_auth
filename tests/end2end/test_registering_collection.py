# -*- coding: utf-8 -*-
"""Test registering collections."""

from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice

from flask import url_for

from xl_auth.collection.models import Collection

from ..factories import CollectionFactory


# noinspection PyUnusedLocal
def test_can_register_new_collection(collection, testapp):
    """Register a new collection."""
    old_count = len(Collection.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Clicks Collections button
    res = res.click('Collections')
    # Clicks Register New Collection button
    res = res.click('Register New Collection')
    # Fills out the form
    form = res.forms['registerCollectionForm']
    form['code'] = 'SfX'
    form['friendly_name'] = 'Important books'
    form['category'] = choice(['uncategorized', 'bibliography', 'library'])
    # Submits
    res = form.submit().follow()
    assert res.status_code == 200
    # A new collection was created
    assert len(Collection.query.all()) == old_count + 1


# noinspection PyUnusedLocal
def test_user_sees_error_message_if_code_is_missing(collection, testapp):
    """Show error if form does not include collection code."""
    # Goes to registration page.
    res = testapp.get(url_for('collection.register'))
    # Fills out form, but omits code.
    form = res.forms['registerCollectionForm']
    form['friendly_name'] = 'Important books'
    form['category'] = choice(['uncategorized', 'bibliography', 'library'])
    # Submits.
    res = form.submit()
    # Sees error message.
    assert 'Code - This field is required.' in res


# noinspection PyUnusedLocal
def test_user_sees_error_message_if_friendly_name_is_missing(collection, testapp):
    """Show error if form does not include Name."""
    # Goes to registration page.
    res = testapp.get(url_for('collection.register'))
    # Fills out form, but omits friendly_name.
    form = res.forms['registerCollectionForm']
    form['code'] = 'SfX'
    form['category'] = choice(['uncategorized', 'bibliography', 'library'])
    # Submits.
    res = form.submit()
    # Sees error message.
    assert 'Name - This field is required.' in res


# noinspection PyUnusedLocal
def test_user_sees_error_message_if_category_is_missing(collection, testapp):
    """Show error if form does not include a valid category."""
    # Goes to registration page.
    res = testapp.get(url_for('collection.register'))
    # Fills out form, but omits category.
    form = res.forms['registerCollectionForm']
    form['code'] = 'SfX'
    form['friendly_name'] = 'Important books'
    # Submits.
    res = form.submit()
    # Sees error message.
    assert 'Category - Not a valid choice' in res


# noinspection PyUnusedLocal
def test_user_sees_error_message_if_collection_already_registered(collection, testapp):
    """Show error if collection already registered."""
    collection = CollectionFactory(active=True)  # A registered collection.
    collection.save()
    # Goes to registration page.
    res = testapp.get(url_for('collection.register'))
    # Fills out form, but collection code is already registered.
    form = res.forms['registerCollectionForm']
    form['code'] = collection.code
    form['friendly_name'] = 'Important books'
    form['category'] = choice(['uncategorized', 'bibliography', 'library'])
    # Submits.
    res = form.submit()
    # Sees error.
    assert 'Code already registered' in res
