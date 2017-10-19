# -*- coding: utf-8 -*-
"""Test registering collections."""

from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice

from flask import url_for
from flask_babel import gettext as _
from jinja2 import escape

from xl_auth.collection.models import Collection

from ..factories import CollectionFactory


def test_superuser_can_register_new_collection(superuser, testapp):
    """Register a new collection."""
    old_count = len(Collection.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Clicks Collections button
    res = res.click(_('Collections'))
    # Clicks Register New Collection button
    res = res.click(_('New Collection'))
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
    # The new collection is listed under existing collections
    collection_id = 'collection-{0}'.format(form['code'].value)
    collection_anchor_xpath = "//a[@class='anchor' and @id='{0}']".format(collection_id)
    assert len(res.lxml.xpath(collection_anchor_xpath)) == 1

    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(form['code'].value))) == 1
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(form['friendly_name'].value))) == 1

    if form['category'].value in {'bibliography', 'library'}:
        assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(
            _(form['category'].value.capitalize())))) == 1
    else:
        assert len(res.lxml.xpath("//td[contains(., '{0}')]/ancestor::tr/td[contains(., '{1}')]"
                                  .format(form['code'].value,
                                          _('No category')))) == 1


# noinspection PyUnusedLocal
def test_superuser_sees_error_message_if_code_is_missing(superuser, collection, testapp):
    """Show error if form does not include collection code."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Goes to registration page.
    res = testapp.get(url_for('collection.register'))
    # Fills out form, but omits code.
    form = res.forms['registerCollectionForm']
    form['friendly_name'] = 'Important books'
    form['category'] = choice(['uncategorized', 'bibliography', 'library'])
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Code'), _('This field is required.')) in res


# noinspection PyUnusedLocal
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
    # Goes to registration page.
    res = testapp.get(url_for('collection.register'))
    # Fills out form, but omits friendly_name.
    form = res.forms['registerCollectionForm']
    form['code'] = 'SfX'
    form['category'] = choice(['uncategorized', 'bibliography', 'library'])
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Name'), _('This field is required.')) in res


# noinspection PyUnusedLocal
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
    # Goes to registration page.
    res = testapp.get(url_for('collection.register'))
    # Fills out form, but omits category.
    form = res.forms['registerCollectionForm']
    form['code'] = 'SfX'
    form['friendly_name'] = 'Important books'
    # Submits.
    res = form.submit()
    # Sees error message.
    assert '{} - {}'.format(_('Category'), _('Not a valid choice')) in res


# noinspection PyUnusedLocal
def test_superuser_sees_error_message_if_collection_already_registered(superuser,
                                                                       collection,
                                                                       testapp):
    """Show error if collection already registered."""
    collection = CollectionFactory(active=True)  # A registered collection.
    collection.save()
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
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
    assert escape(_('Code "%(code)s" already registered', code=collection.code)) in res


def test_user_cannot_register_collection(user, collection, testapp):
    """Attempt to register a collection."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # We click the Collections button
    res = res.click(_('Collections'))

    # No New Collection button for regular users
    assert res.lxml.xpath("//a[contains(@text,'{0}')]".format(_('New Collection'))) == []

    # Try to go directly to register
    testapp.get('/collections/register/', status=403)
