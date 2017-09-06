# xl_auth

OAuth2 authentication for LibrisXL, replacing BibDB counterpart.


## Project Notes

Technology choices:

* [libsodium](https://download.libsodium.org/doc/) and 
  [Argon2](https://en.wikipedia.org/wiki/Argon2) for hashing
* Early-on Docker integration for easy testing during ahead of first
  stable release
* Review [Beyond PEP-8](https://www.youtube.com/watch?v=wf-BqAjZb8M) for
  inspiration with respect to code style
* Solution implemented as Gunicorn-Flask application, intended to
  run behind Nginx reverse-proxying for production and 
  utilizing [Flask-OAuthlib](https://flask-oauthlib.readthedocs.io/en/latest/)
  for OAuth2 support
* Python 3.6 strongly preferred, but should probably run on 2.7 as well
* Jenkins multi-branch declarative pipeline for CI during development
* The production database of choice is Postgres, using SQLAlchemy PostgreSQL
  Engine
* DB migration support, probably we should go with
  [Alembic](http://alembic.zzzcomputing.com/en/latest/)


## Changelog

### v. 0.1

* Establishing initial project requirements, with none of 
  the intended functionality in place

