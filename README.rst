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

Local dev deployment ::

    export FLASK_DEBUG=0
    export SQLALCHEMY_DATABASE_URI=postgresql://localhost/db')
    npm run build    # build assets with webpack
    flask translate  # compile translations
    flask run        # start the flask server

In your production environment, make sure the ``FLASK_DEBUG`` environment variable is set to ``0``,
so that ``ProdConfig`` is used.

Staging dev deployment ::

    cd ansible/
    vagrant up --provision

Rolling out latest Docker on login.libris.kb.se dev server ::

    cd ansible/
    ansible-playbook deployment.yml -u <my-exchange-username> --ask-pass --ask-become-pass

For creating an initial admin account during provisioning, with username libris@kb.se,
append ``-e xl_auth_admin_pass=my-secret-password`` to the Ansible invocation.


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

The latest application build can be built and run using Docker for testing purposes ::

    docker build -t mblomdahl/xl_auth .
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

v. 0.5.5
--------

* Bug fix for OAuth2 token handling


v. 0.5.4
--------

* UI fixes for OAuth2 authorization view
* Bug fix for ``/oauth/token`` API endpoint


v. 0.5.3
--------

* Add collection name to ``/oauth/verify`` response
* Fix broken database migration (`#68 <https://github.com/libris/xl_auth/issues/68>`_)


v. 0.5.2
--------

* Add ``app_version`` property to response from OAuth2 API endpoints
* Bug fixes for OAuth2 data model; fully re-created on ``flask db upgrade``
  (`#68 <https://github.com/libris/xl_auth/issues/68>`_)
* Updated Voyager/SysAdmin data import (`#38 <https://github.com/libris/xl_auth/issues/38>`_)


v. 0.5.1
--------

* Update ``/oauth/verify`` API response format
  (`#68 <https://github.com/libris/xl_auth/issues/68>`_)
* Fix bug where collections would read the wrong active/inactive state from bibdb.libris.kb.se


v. 0.5.0
--------

* Introduced buggy and limited OAuth2 provider
  (`#68 <https://github.com/libris/xl_auth/issues/68>`_)
* Updated Voyager/SysAdmin data import (`#38 <https://github.com/libris/xl_auth/issues/38>`_)


v. 0.4.6
--------

* Minor traceability improvements (`#78 <https://github.com/libris/xl_auth/issues/78>`_)


v. 0.4.5
--------

* Bug fixes (`#75 <https://github.com/libris/xl_auth/issues/75>`_,
  `#76 <https://github.com/libris/xl_auth/issues/76>`_)


v. 0.4.4
--------

* Data import updates (`#44 <https://github.com/libris/xl_auth/issues/44>`_)
* UI adjustments; irrelevant permissions no longer shown to cataloging admins, using
  term "sigel" instead of "kod"
* Ansible provisioning updated to use Nginx reverse proxy and SSL
  (`#39 <https://github.com/libris/xl_auth/issues/39>`_)


v. 0.4.3
--------

* Personalized user icons (Gravatar, `#70 <https://github.com/libris/xl_auth/issues/70>`_)
* Updated ``/about/`` page with current version number + links
  (`#71 <https://github.com/libris/xl_auth/issues/71>`_)
* Only list permissions on active collections on ``/users/profile/`` page


v. 0.4.2
--------

* UI improvements (`#61 <https://github.com/libris/xl_auth/issues/61>`_)
* Updated data import (`#38 <https://github.com/libris/xl_auth/issues/38>`_)


v. 0.4.1
--------

* Event stricter restrictions on non-admin users
  (`#48 <https://github.com/libris/xl_auth/issues/48>`_)
* Improved Ansible deployment logic for login.libris.kb.se
  (`#39 <https://github.com/libris/xl_auth/issues/39>`_)
* UI and help text improvements


v. 0.4.0
--------

* Added ``flask import_data`` CLI tool for pulling data from legacy systems
  (`#38 <https://github.com/libris/xl_auth/issues/38>`_,
  `#43 <https://github.com/libris/xl_auth/issues/43>`_)
* Styling and usability improvements (`#6 <https://github.com/libris/xl_auth/issues/6>`_,
  `#22 <https://github.com/libris/xl_auth/issues/22>`_)
* Applied restrictions on anonymous users and non-admins
  (`#48 <https://github.com/libris/xl_auth/issues/48>`_)
* Added new type of permission, "being the cataloging admin for a collection"
  (`#40 <https://github.com/libris/xl_auth/issues/40>`_)
* Support for dev deployment on login.libris.kb.se
  (`#39 <https://github.com/libris/xl_auth/issues/39>`_)


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
