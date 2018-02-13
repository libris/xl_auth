#  -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from re import match
from os import path
from setuptools import setup, find_packages

#from xl_auth import __name__, __version__


#def _read_files_from_root_dir(*filenames):
#    """Open and read *filenames* from project root dir."""
#
#    return '\n'.join([open(path.join(path.dirname(__file__), filename)).read()
#                      for filename in filenames])


setup(
    entry_points={
        'console_scripts': [
            'xl-auth-flask-cli=xl_auth.entrypoint:main',
        ]
    },
    #name=__name__,
    #version=__version__,
    #packages=find_packages(include=('xl_auth.*', 'autoapp')),
    #include_package_data=True,
    #package_data={
    #    #'': ['autoapp.py'],
    #    '': ['translations/sv/LC_MESSAGES/*', 'templates/*.html']
    #},
    #license='Apache-2.0',
    #package_dir={'': 'src'},
    #package_data={'': ['*.json']},
    #data_files=[('lib/python2.7/site-packages/{0}'.format(package_name), ['build.properties'])],
    #include_package_data=True,
    #description='Authorization and OAuth2 provider for LibrisXL',
    #long_description=_read_files_from_root_dir('README.rst'),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    setup_requires=[
        'setuptools==38.5.1'
    ],
    dependency_links=[
        "git+https://github.com/libris/wtforms#egg=WTForms-3.0.0"
    ],
    platforms=['POSIX'],
    zip_safe=False
)
