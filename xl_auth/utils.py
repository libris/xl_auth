# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""

from __future__ import absolute_import, division, print_function, unicode_literals

import hashlib

from flask import flash


def flash_errors(form, category='warning'):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash('{0} - {1}'.format(getattr(form, field).label.text, error), category)


def get_gravatar_url(user_email, size):
    """Get gravatar url from user email."""
    clean_email = str(user_email).lower()
    hash = hashlib.md5(clean_email)
    url = 'https://www.gravatar.com/avatar/' + hash.hexdigest() + '?d=mm&s=' + str(size)
    return url
