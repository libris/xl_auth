# -*- coding: utf-8 -*-
"""Test listing tokens."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import url_for


def test_superuser_can_list_existing_token(superuser, token, testapp):
    """List existing tokens."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # Clicks Token button
    # res = res.click(href=url_for('token.home'))
    # FIXME: No nav link yet
    assert res.lxml.xpath("//a[contains(@href,'{0}')]".format(url_for('token.home'))) == []

    res = testapp.get('/tokens/')

    # The token is listed under existing tokens
    # token.id shows up twice, once alone in a cell, once in a delete link
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(token.id))) == 2
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(token.user.email))) == 1
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(token.client.name))) == 1


def test_user_cannot_list_existing_token(user, testapp):
    """Attempt to list existing tokens."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # No Token home link for regular users
    assert res.lxml.xpath("//a[contains(@href,'{0}')]".format(url_for('token.home'))) == []

    # Try to go there directly
    testapp.get(url_for('token.home'), status=403)
