.. -*- coding: utf-8 -*-

=========
 xl_auth
=========

OAuth2 authentication for LibrisXL, replacing BibDB counterpart.



Project Notes
=============

Technology choices:

* `libsodium <https://download.libsodium.org/doc/>`_ and
  `Argon2 <https://en.wikipedia.org/wiki/Argon2>`_ for hashing
* Early-on Docker integration for easy testing during ahead of first
  stable release
* Review `Beyond PEP-8 <https://www.youtube.com/watch?v=wf-BqAjZb8M>`_ for
  inspiration with respect to code style
* Solution implemented as Gunicorn-Flask application, intended to
  run behind Nginx reverse-proxying for production and
  utilizing `Flask-OAuthlib <https://flask-oauthlib.readthedocs.io/en/latest/>`_
  for OAuth2 support
* Python 3.6 strongly preferred, but should probably run on 2.7 as well
* Jenkins multi-branch declarative pipeline for CI during development
* The production database of choice is Postgres, using SQLAlchemy PostgreSQL
  Engine
* DB migration support, probably we should go with
  `Alembic <http://alembic.zzzcomputing.com/en/latest/>`_



DB Models
---------

User:

* Email
* Full name
* Password (Argon2/bcrypt/scrypt + salt (libsodium))
* User role (admin, etc.)

Collection:

* Code ("S") - unique
* Name ("Kungliga biblioteket")
* Category (library/bibliography/?)
* "Active" (bool?)

Access rights:

* User ID
* Collection ID
* 'kat'|'reg'



Development Environment
=======================

Getting started with a fresh virtualenv:

.. sourcecode:: bash

    virtualenv venv && source venv/bin/activate
    pip install -r requirements.txt


Running tests:

.. sourcecode:: bash

    make clean test lint coverage


Building the documentation:

.. sourcecode:: bash

    make docs



Changelog
=========

v. 0.1
------

* Establishing initial project requirements, with none of
  the intended functionality in place

