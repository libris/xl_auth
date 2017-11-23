# -*- coding: utf-8 -*-
"""OAuth Client models."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

from six import string_types
from sqlalchemy.ext.hybrid import hybrid_property

from ...database import Column, Model, db, reference_col, relationship


class Client(Model):
    """An OAuth2 Client."""

    __tablename__ = 'clients'
    client_id = Column(db.String(32), primary_key=True)
    client_secret = Column(db.String(256), unique=True, nullable=False)

    is_confidential = Column(db.Boolean(), default=True, nullable=False)

    _redirect_uris = Column(db.Text(), nullable=False)
    _default_scopes = Column(db.Text(), nullable=False)

    # Human readable info fields
    name = Column(db.String(64), nullable=False)
    description = Column(db.String(400), nullable=False)

    modified_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                         nullable=False)
    modified_by_id = reference_col('users', nullable=False)
    modified_by = relationship('User', foreign_keys=modified_by_id)

    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = reference_col('users', nullable=False)
    created_by = relationship('User', foreign_keys=created_by_id)

    def __init__(self, redirect_uris=None, default_scopes=None, **kwargs):
        """Create instance."""
        client_id = Client._get_rand_hex_str(32)
        client_secret = Client._get_rand_hex_str(256)
        db.Model.__init__(self, client_id=client_id, client_secret=client_secret, **kwargs)
        self.redirect_uris = redirect_uris
        self.default_scopes = default_scopes

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        # noinspection PyUnresolvedReferences
        return cls.query.filter_by(client_id=record_id).first()

    @hybrid_property
    def client_type(self):
        """Return client type."""
        if self.is_confidential:
            return 'confidential'
        else:
            return 'public'

    @hybrid_property
    def redirect_uris(self):
        """Return redirect URIs list."""
        return self._redirect_uris.split(' ')

    @redirect_uris.setter
    def redirect_uris(self, value):
        """Store redirect URIs list as string."""
        if isinstance(value, string_types):
            self._redirect_uris = value
        elif isinstance(value, list):
            self._redirect_uris = ' '.join(value)
        else:
            self._redirect_uris = value

    @hybrid_property
    def default_redirect_uri(self):
        """Return default redirect URI."""
        return self.redirect_uris[0]

    @hybrid_property
    def default_scopes(self):
        """Return default scopes list."""
        return self._default_scopes.split(' ')

    @default_scopes.setter
    def default_scopes(self, value):
        """Store default scopes list as string."""
        if isinstance(value, string_types):
            self._default_scopes = value
        elif isinstance(value, list):
            self._default_scopes = ' '.join(value)
        else:
            self._default_scopes = value

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Client({name!r})>'.format(name=self.name)
