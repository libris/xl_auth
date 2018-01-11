# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import flash, request

try:
    # noinspection PyCompatibility
    from urlparse import urlparse, urljoin
except ImportError:
    # noinspection PyCompatibility
    from urllib.parse import urlparse, urljoin


def flash_errors(form, category='warning'):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash('{0} - {1}'.format(getattr(form, field).label.text, error), category)


def get_redirect_target():
    """Return safe redirect URL, from `<http://flask.pocoo.org/snippets/62/>`_."""
    for target in [request.form.get('next_redirect'), request.values.get('next')]:
        if not target:
            continue
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        if test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc:
            return target
    else:
        return ''


def get_remote_addr():
    """Return remote IP address for current request."""
    if 'X-Real-IP' in request.headers:
        return request.headers['X-Real-IP']
    else:
        return request.remote_addr
