#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
    print_function, absolute_import, unicode_literals, division)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from xl_auth import __name__, __version__


def _get_readme_contents():
    """Read *README.rst* from project root dir."""

    with open('README.rst') as readme_file:
        return readme_file.read()


setup(
    name=__name__,
    version=__version__,
    url='https://github.com/libris/xl_auth',
    license='Apache',
    author='Mats Blomdahl',
    author_email='mats.blomdahl@gmail.com',
    description='Oauth2 provider for National Library of Sweden',
    long_description=_get_readme_contents(),
    keywords='librisxl',
    packages=['xl_auth'],
    package_dir={'xl_auth': 'xl_auth'},
    entry_points={
        'console_scripts': [
            'xl_auth-ping = xl_auth.scripts.say_pong',
            'xl_auth-wsgi = xl_auth.scripts.run_wsgi'
        ]
    },
    install_requires=[
        'Flask>=0.12',
        'Flask-Oauthlib>=0.9'
    ],
    tests_requires=[
        'mock>=2.0',
        'testfixtures>=5.2'
    ],
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
    # https://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Environment :: Console',
        'Framework :: Flask',
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 2.7'
        'Programming Language :: Python :: 3.6'
    ],
    platforms=['POSIX']
)
