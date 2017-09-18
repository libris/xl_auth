.. -*- coding: utf-8 -*-

=========
 xl_auth
=========

OAuth2 authorization for LibrisXL, replacing BibDB counterpart.

.. image:: http://jenkins.smithmicro.io:8080/job/xl_auth-multibranch/job/master/lastBuild/badge/icon
    :target: http://jenkins.smithmicro.io:8080/job/xl_auth-multibranch/job/master/lastBuild/
    :alt: Build Status


Quickstart
==========

First, set your app's secret key as an environment variable. For example,
add the following to ``.bashrc`` or ``.bash_profile``.

.. code-block:: bash

    export XL_AUTH_SECRET='something-really-secret'

Run the following commands to bootstrap your environment ::

    git clone https://github.com/libris/xl_auth
    cd xl_auth
    virtualenv venv && source venv/bin/activate
    pip install -r requirements/dev.txt
    npm install
    npm start  # run webpack dev server and flask server using concurrently

You will see a pretty welcome screen.

In general, before running shell commands, set the ``FLASK_APP`` and
``FLASK_DEBUG`` environment variables ::

    export FLASK_APP=/path/to/autoapp.py
    export FLASK_DEBUG=1

Once you have installed your DBMS, run the following to create your app's
database tables and perform the initial migration ::

    flask db init
    flask db migrate
    flask db upgrade
    npm start


Deployment
==========

To deploy ::

    export FLASK_DEBUG=0
    npm run build   # build assets with webpack
    flask run       # start the flask server

In your production environment, make sure the ``FLASK_DEBUG`` environment
variable is unset or is set to ``0``, so that ``ProdConfig`` is used.


Shell
=====

To open the interactive shell, run ::

    flask shell

By default, you will have access to the flask ``app``.


Running Tests
=============

To run all tests, run ::

    flask test


Migrations
==========

Whenever a database migration needs to be made. Run the following commands ::

    flask db migrate

This will generate a new migration script. Then run ::

    flask db upgrade

To apply the migration.

For a full migration command reference, run ``flask db --help``.


Asset Management
================

Files placed inside the ``assets`` directory and its subdirectories
(excluding ``js`` and ``css``) will be copied by webpack's
``file-loader`` into the ``static/build`` directory, with hashes of
their contents appended to their names.  For instance, if you have the
file ``assets/img/favicon.ico``, this will get copied into something
like ``static/build/img/favicon.fec40b1d14528bf9179da3b6b78079ad.ico``.
You can then put this line into your header ::

    <link rel="shortcut icon" href="{{asset_url_for('img/favicon.ico') }}">

to refer to it inside your HTML page.  If all of your static files are
managed this way, then their filenames will change whenever their
contents do, and you can ask Flask to tell web browsers that they
should cache all your assets forever by including the following line
in your ``settings.py`` ::

    SEND_FILE_MAX_AGE_DEFAULT = 31556926  # one year


Docker
======

The latest application build can be deployed using Docker for testing purposes ::

    docker run -it -p 5000:5000 mblomdahl/xl_auth


All Flask command-line tools are accessed by optional input argument to the container, e.g.
``flask shell -> docker run -it ...ahl/auth shell``, ``flask db -> docker run -it ...ahl/auth db``.


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


Changelog
=========

v. 0.1.0
--------

* Establishing initial project requirements, with none of
  the intended functionality in place

