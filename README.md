# xl_auth

Authorization and OAuth2 provider for LibrisXL.

## Quickstart

First, set your app's secret key as an environment variable. For
example, add the following to `.bashrc` or `.bash_profile`.

``` bash
export XL_AUTH_SECRET='something-really-secret'
```

Run the following commands to bootstrap your environment:

    git clone https://github.com/libris/xl_auth
    cd xl_auth
    python3 -m venv venv && source venv/bin/activate
    pip install wheel
    pip install -r requirements/dev.txt
    npm install
    export FLASK_APP=$(pwd)/autoapp.py
    export FLASK_DEBUG=1
    npm run build
    flask db upgrade
    flask create-user --email me@example.com -p password --is-admin --is-active
    npm start  # run webpack dev server and flask server using concurrently

You will see a pretty welcome screen.

In general, before running flask shell commands, set the `FLASK_APP` and
`FLASK_DEBUG` environment variables:

    export FLASK_APP=/path/to/autoapp.py
    export FLASK_DEBUG=1

Setting FLASK_DEBUG=1 will tell the application to use `DevConfig` as
specified in ./xl_auth/settings.py. This configuration sets up a SQLite
db for development and points the SQLALCHEMY_DATABASE_URI environment
variable to this db.

## Shell

To open the interactive shell, run:

    flask shell

By default, you will have access to the flask `app`.

## Localization

To compile Swedish localization support using Babel, run:

    flask translate

_Note_: Might fail with a `RuntimeError` if your shell env is set to
use ASCII. Solve it like so:

    export LC_ALL=sv_SE.UTF-8
    export LANG=sv_SE.UTF-8

## Running Tests

To run all tests, run :

    flask test

## Migrations

Whenever a database migration needs to be made. Run the following commands:

    flask db migrate

This will generate a new migration script. Then run:

    flask db upgrade

To apply the migration.

For a full migration command reference, run `flask db --help`.

## Asset Management

Files placed inside the `assets` directory and its subdirectories
(excluding `js` and `css`) will be copied by webpack\'s `file-loader`
into the `static/build` directory, with hashes of their contents
appended to their names.

For instance, if you have a file `assets/img/favicon.ico`, this will get
copied into something like
`static/build/img/favicon.fec40b1d14528bf9179da3b6b78079ad.ico`.

You can then put this line into your header:

    <link rel="shortcut icon" href="{{ static_url_for('static', 'filename=img/favicon.ico') }}">

to refer to it inside your HTML page. If all of your static files are
managed this way, then their filenames will change whenever their
contents do, and you can ask Flask to tell web browsers that they should
cache all your assets forever by including the following line in your
`settings.py` :

    SEND_FILE_MAX_AGE_DEFAULT = 31556926  # one year

## Docker

The latest application build can be built and run using Docker for
testing purposes:

    docker build -t xl_auth .
    docker run -it -p 5000:5000 xl_auth

All Flask command-line tools are accessed by optional input argument to
the container, e.g. `flask shell -> docker run -it xl_auth shell`,
`flask db -> docker run -it xl_auth db`.

Create a user:

    docker exec -it xl_auth /usr/local/bin/flask create-user -e me@kb.se -p 1234 --force \
        --is-admin --is-active
    # Now open localhost:5000 in the browser and login as me@kb.se

To import users, collections and permissions into the Docker container,
run:

    docker exec -it xl_auth /usr/local/bin/flask import-data --admin-email=libris@kb.se

## Project Notes

Technology choices:

-   `libsodium` and [Argon2](https://en.wikipedia.org/wiki/Argon2) for
    hashing?
-   Early-on Docker integration for easy testing during ahead of first
    stable release
-   Solution implemented as Gunicorn-Flask application, intended to run
    behind Nginx reverse-proxying in production and utilizing
    [Flask-OAuthlib](https://flask-oauthlib.readthedocs.io/en/latest/)
    for OAuth2 support
-   Python 3.6 strongly preferred, but should probably run on 2.7 as
    well
-   Jenkins multi-branch declarative pipeline for CI during development
-   The production database of choice is Postgres, using SQLAlchemy
    PostgreSQL Engine

## DB Models

![DB model](https://user-images.githubusercontent.com/51744858/60274493-6bd5dd00-98f8-11e9-889f-e7527add8745.png)

## Changelog

### v. 1.10.0 (unreleased)

- Bump dependencies to make xl_auth work with newer (3.9+) versions of Python
- Make Dockerfile work again
- Update README; remove outdated things
- Remove old, unused Ansible files
- Remove old, unused docker-compose file
- Convert README from rst to Markdown


### v. 1.9.0

-   Include user id in [/verify]{.title-ref} response

### v. 1.8.3

Bump dependencies

### v. 1.8.2

-   CSS fixes

### v. 1.8.1

-   Bump version number

### v. 1.8.0

-   Soft-delete users in web interface and using [flask
    soft-delete-user]{.title-ref}; support changing user email address

### v. 1.7.1

-   Make locally stored token lifetime explicit

### v. 1.7.0

-   Adaptions to run with Python 3 and Postgres 13
-   Bump dependencies and fix security warnings

### v. 1.6.0

-   Update/remove links related to GDPR/Libris info and support

### v. 1.5.0

-   Add \'Global Registrant\' permission type

### v. 1.4.0

-   Clarify copy

### v. 1.3.0

-   Add support for OAuth2 Backend Application FLow

### v. 1.2.0

-   Update ToS page

### v. 1.1.0

-   Add GDPR information

### v. 1.0.0

-   Allow cataloging admins to create and edit cataloging admin
    permissions
-   Save scope authorization in user session
-   Allow CORS requests

### v. 0.8.0

-   Add support for OAuth2 implicit flow

### v. 0.7.8

-   Add CLI tool for purging a user from the system
    ([#148](https://github.com/libris/xl_auth/issues/148))
-   Clean up Jenkinsfile

### v. 0.7.7

-   Replace Docker container runtimes with local installs of xl_auth and
    Postgres ([#178](https://github.com/libris/xl_auth/issues/178))
-   Copy improvements / UX
    ([#176](https://github.com/libris/xl_auth/issues/176),
    [#173](https://github.com/libris/xl_auth/issues/173))

### v. 0.7.6

-   Production hardening
    ([#179](https://github.com/libris/xl_auth/issues/179),
    [#175](https://github.com/libris/xl_auth/issues/175),
    [#174](https://github.com/libris/xl_auth/issues/174))

### v. 0.7.5

-   Security improvements
    ([#154](https://github.com/libris/xl_auth/issues/154),
    [#155](https://github.com/libris/xl_auth/issues/155))
-   UX enhancements
    ([#114](https://github.com/libris/xl_auth/issues/114))
-   Monitoring of Nginx logs
    ([#157](https://github.com/libris/xl_auth/issues/157))

### v. 0.7.4

-   UX enhancements
    ([#128](https://github.com/libris/xl_auth/issues/128),
    [#151](https://github.com/libris/xl_auth/issues/151))

### v. 0.7.3

-   UX enhancements
    ([#149](https://github.com/libris/xl_auth/issues/149),
    [#146](https://github.com/libris/xl_auth/issues/146))

### v. 0.7.2

-   Added support for creating new users directly from register/edit
    permission views
    ([#140](https://github.com/libris/xl_auth/issues/140))
-   UX enhancements
    ([#142](https://github.com/libris/xl_auth/issues/142),
    [#133](https://github.com/libris/xl_auth/issues/133))
-   Link to Permissions\' overview removed from navbar
-   Ignoring/discarding permissions on inactive collections

### v. 0.7.1

-   Revised API endpoints for registering/editing permissions; now
    allowing cataloging admins to register new and edit existing
    permissions on their collections
    ([#126](https://github.com/libris/xl_auth/issues/126))
-   UX enhancements
    ([#129](https://github.com/libris/xl_auth/issues/129),
    [#134](https://github.com/libris/xl_auth/issues/134),
    [#131](https://github.com/libris/xl_auth/issues/131),
    [#130](https://github.com/libris/xl_auth/issues/130))

### v. 0.7.0

-   Preserve permissions created by others than <libris@kb.se> superuser
-   Revised API endpoint for deleting permissions; now allowing
    cataloging admins to delete permissions on their collections
    ([#123](https://github.com/libris/xl_auth/issues/123))

### v. 0.6.4

-   Provisioning and stability updates
    ([#121](https://github.com/libris/xl_auth/issues/121),
    [#122](https://github.com/libris/xl_auth/issues/122))

### v. 0.6.3

-   Added \"view collection\" link to user profile page
-   *Terms of Service* view added, requesting the user to approve
    ([#112](https://github.com/libris/xl_auth/issues/112))
-   Bug fix for loading Voyager permissions on SEK
    ([#113](https://github.com/libris/xl_auth/issues/113))
-   Bug fix for permissions exchange with LibrisXL
    ([#110](https://github.com/libris/xl_auth/issues/110))

### v. 0.6.2

-   Secret usability improvements for admin interface

### v. 0.6.1

-   Under-the-hood traceability updates
    ([#78](https://github.com/libris/xl_auth/issues/78))

### v. 0.6.0

-   Added support for resetting forgotten user account passwords
    ([#41](https://github.com/libris/xl_auth/issues/41))
-   When registering new user accounts, opting in for a password reset
    email is the preferred way of enabling them to login
    ([#102](https://github.com/libris/xl_auth/issues/102))

### v. 0.5.8

-   Update internal links to reference users by ID instead of email
    ([#25](https://github.com/libris/xl_auth/issues/25))
-   Refactored OAuth2 (internal) paths

### v. 0.5.7

-   Reuse existing OAuth2 tokens on refresh

### v. 0.5.6

-   Fix broken 0.5.5 build

### v. 0.5.5

-   Bug fix for OAuth2 token handling

### v. 0.5.4

-   UI fixes for OAuth2 authorization view
-   Bug fix for `/oauth/token` API endpoint

### v. 0.5.3

-   Add collection name to `/oauth/verify` response
-   Fix broken database migration
    ([#68](https://github.com/libris/xl_auth/issues/68))

### v. 0.5.2

-   Add `app_version` property to response from OAuth2 API endpoints
-   Bug fixes for OAuth2 data model; fully re-created on
    `flask db upgrade`
    ([#68](https://github.com/libris/xl_auth/issues/68))
-   Updated Voyager/SysAdmin data import
    ([#38](https://github.com/libris/xl_auth/issues/38))

### v. 0.5.1

-   Update `/oauth/verify` API response format
    ([#68](https://github.com/libris/xl_auth/issues/68))
-   Fix bug where collections would read the wrong active/inactive state
    from bibdb.libris.kb.se

### v. 0.5.0

-   Introduced buggy and limited OAuth2 provider
    ([#68](https://github.com/libris/xl_auth/issues/68))
-   Updated Voyager/SysAdmin data import
    ([#38](https://github.com/libris/xl_auth/issues/38))

### v. 0.4.6

-   Minor traceability improvements
    ([#78](https://github.com/libris/xl_auth/issues/78))

### v. 0.4.5

-   Bug fixes ([#75](https://github.com/libris/xl_auth/issues/75),
    [#76](https://github.com/libris/xl_auth/issues/76))

### v. 0.4.4

-   Data import updates
    ([#44](https://github.com/libris/xl_auth/issues/44))
-   UI adjustments; irrelevant permissions no longer shown to cataloging
    admins, using term \"sigel\" instead of \"kod\"
-   Ansible provisioning updated to use Nginx reverse proxy and SSL
    ([#39](https://github.com/libris/xl_auth/issues/39))

### v. 0.4.3

-   Personalized user icons (Gravatar,
    [#70](https://github.com/libris/xl_auth/issues/70))
-   Updated `/about/` page with current version number + links
    ([#71](https://github.com/libris/xl_auth/issues/71))
-   Only list permissions on active collections on `/users/profile/`
    page

### v. 0.4.2

-   UI improvements ([#61](https://github.com/libris/xl_auth/issues/61))
-   Updated data import
    ([#38](https://github.com/libris/xl_auth/issues/38))

### v. 0.4.1

-   Event stricter restrictions on non-admin users
    ([#48](https://github.com/libris/xl_auth/issues/48))
-   Improved Ansible deployment logic for login.libris.kb.se
    ([#39](https://github.com/libris/xl_auth/issues/39))
-   UI and help text improvements

### v. 0.4.0

-   Added `flask import-data` CLI tool for pulling data from legacy
    systems ([#38](https://github.com/libris/xl_auth/issues/38),
    [#43](https://github.com/libris/xl_auth/issues/43))
-   Styling and usability improvements
    ([#6](https://github.com/libris/xl_auth/issues/6),
    [#22](https://github.com/libris/xl_auth/issues/22))
-   Applied restrictions on anonymous users and non-admins
    ([#48](https://github.com/libris/xl_auth/issues/48))
-   Added new type of permission, \"being the cataloging admin for a
    collection\" ([#40](https://github.com/libris/xl_auth/issues/40))
-   Support for dev deployment on login.libris.kb.se
    ([#39](https://github.com/libris/xl_auth/issues/39))

### v. 0.3.0

-   Added the concept of users having permissions on zero or more
    collections ([#27](https://github.com/libris/xl_auth/issues/27))

### v. 0.2.2

-   Bug fix for uniqueness checks on email addresses and collection
    codes ([#30](https://github.com/libris/xl_auth/issues/30))

### v. 0.2.1

-   Added localization for Swedish and set it as the default
    `BABEL_DEFAULT_LOCALE`
    ([#17](https://github.com/libris/xl_auth/issues/17))
-   Added support for editing users
    ([#19](https://github.com/libris/xl_auth/issues/19))

### v. 0.2.0

-   Replaced project template with
    <https://github.com/sloria/cookiecutter-flask>
-   Basic functionality of registering a user by email address and
    logging in
-   A simple form of \"collections\" can be added and edited
-   Dockerfile added for testing purposes (running Flask in debug mode
    with a ephemeral SQLite db)
-   Jenkinsfile (multibranch pipeline) added for
    testing/linting/building on any code changes

### v. 0.1.0

-   Establishing initial project requirements, with none of the intended
    functionality in place
