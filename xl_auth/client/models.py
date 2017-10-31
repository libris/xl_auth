# -*- coding: utf-8 -*-
"""Client models."""

from __future__ import absolute_import, division, print_function, unicode_literals

from codecs import getencoder
from os import urandom

from ..database import Column, Model, SurrogatePK, db


class Client(SurrogatePK, Model):
    """An OAuth2 Client."""

    __tablename__ = 'clients'
    client_id = Column(db.String(64), unique=True, nullable=False)
    client_secret = Column(db.String(256), unique=True, nullable=False)

    created_by = Column(db.ForeignKey('users.id'), nullable=False)

    is_confidential = Column(db.Boolean(), default=True, nullable=False)

    redirect_uris = Column(db.Text(), nullable=False)
    default_scopes = Column(db.Text(), nullable=False)

    # Human readable info fields
    name = Column(db.String(64))
    description = Column(db.String(400))

    def __init__(self, **kwargs):
        """Create instance."""
        client_id = Client._generate_client_id()
        client_secret = Client._generate_client_secret()
        db.Model.__init__(self, client_id=client_id, client_secret=client_secret, **kwargs)

    @staticmethod
    def _generate_client_id():
        return getencoder('hex')(urandom(64))[0].decode('utf-8')[:8]

    @staticmethod
    def _generate_client_secret():
        return getencoder('hex')(urandom(256))[0].decode('utf-8')[:16]

    @property
    def client_type(self):
        """Return client type."""
        if self.is_confidential:
            return 'confidential'
        else:
            return 'public'

    @property
    def default_redirect_uri(self):
        """Return default redirect URI."""
        return self.redirect_uris.split()[0]

    def validate_scopes(self, scopes):
        """Validate scopes."""
        client_scopes = set(self.default_scopes.split())
        return client_scopes.issuperset(set(scopes))

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Client({name!r})>'.format(name=self.name)
