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
  run behind Nginx reverse-proxying for production
* Python 3.6 strongly preferred, but should probably run on 2.7 as well
* Jenkins multi-branch declarative pipeline for CI during development

