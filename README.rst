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
    npm build
    export FLASK_APP=$(PWD)/autoapp.py
    export FLASK_DEBUG=1
    flask db upgrade
    flask create_user --email me@example.com --is-admin
    npm start  # run webpack dev server and flask server using concurrently

You will see a pretty welcome screen.

In general, before running flask shell commands, set the ``FLASK_APP`` and
``FLASK_DEBUG`` environment variables ::

    export FLASK_APP=/path/to/autoapp.py
    export FLASK_DEBUG=1


Deployment
==========

To deploy ::

    export FLASK_DEBUG=0
    npm run build    # build assets with webpack
    flask translate  # compile translations
    flask run        # start the flask server

In your production environment, make sure the ``FLASK_DEBUG`` environment variable is
unset or is set to ``0``, so that ``ProdConfig`` is used.


Shell
=====

To open the interactive shell, run ::

    flask shell

By default, you will have access to the flask ``app``.


Localization
============

To compile Swedish localization support using Babel, run ::

    flask translate


.. note::

    Might fail with a `RuntimeError` if your shell env is set to use ASCII. Solve it like so ::

        export LC_ALL=sv_SE.UTF-8
        export LANG=sv_SE.UTF-8


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

Files placed inside the ``assets`` directory and its subdirectories (excluding ``js`` and ``css``)
will be copied by webpack's ``file-loader`` into the ``static/build`` directory, with hashes of
their contents appended to their names.

For instance, if you have a file ``assets/img/favicon.ico``, this will get copied into something
like ``static/build/img/favicon.fec40b1d14528bf9179da3b6b78079ad.ico``.

You can then put this line into your header ::

    <link rel="shortcut icon" href="{{ asset_url_for('img/favicon.ico') }}">

to refer to it inside your HTML page.  If all of your static files are managed this way, then
their filenames will change whenever their contents do, and you can ask Flask to tell web browsers
that they should cache all your assets forever by including the following line in
your ``settings.py`` ::

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

* ``libsodium`` and `Argon2 <https://en.wikipedia.org/wiki/Argon2>`_ for hashing?
* Early-on Docker integration for easy testing during ahead of first stable release
* Solution implemented as Gunicorn-Flask application, intended to run behind Nginx reverse-proxying
  in production and utilizing `Flask-OAuthlib <https://flask-oauthlib.readthedocs.io/en/latest/>`_
  for OAuth2 support
* Python 3.6 strongly preferred, but should probably run on 2.7 as well
* Jenkins multi-branch declarative pipeline for CI during development
* The production database of choice is Postgres, using SQLAlchemy PostgreSQL Engine


DB Models
---------

.. image:: https://user-images.githubusercontent.com/18367829/30987221-8a1834d2-a496-11e7-8a54-27f00a24da7d.png
    :target: https://github.com/libris/xl_auth/pull/33
    :alt: screen shot 2017-09-28 at 9 42 42 pm


Changelog
=========

v. 0.3.0
--------

* Added the concept of users having permissions on zero or more collections
  (`#27 <https://github.com/libris/xl_auth/issues/27>`_)


v. 0.2.2
--------

* Bug fix for uniqueness checks on email addresses and collection codes
  (`#30 <https://github.com/libris/xl_auth/issues/30>`_)


v. 0.2.1
--------

* Added localization for Swedish and set it as the default ``BABEL_DEFAULT_LOCALE``
  (`#17 <https://github.com/libris/xl_auth/issues/17>`_)
* Added support for editing users (`#19 <https://github.com/libris/xl_auth/issues/19>`_)


v. 0.2.0
--------

* Replaced project template with `<https://github.com/sloria/cookiecutter-flask>`_
* Basic functionality of registering a user by email address and logging in
* A simple form of "collections" can be added and edited
* Dockerfile added for testing purposes (running Flask in debug mode with a ephemeral SQLite db)
* Jenkinsfile (multibranch pipeline) added for testing/linting/building on any code changes


v. 0.1.0
--------

* Establishing initial project requirements, with none of the intended functionality in place
