# -*- coding: utf-8 -*-
"""Token models."""

from __future__ import absolute_import, division, print_function, unicode_literals

from codecs import getencoder
from datetime import datetime, timedelta
from os import urandom

from ..database import Column, Model, SurrogatePK, db, reference_col, relationship


class Token(SurrogatePK, Model):
    """An OAuth2 Bearer token."""

    __tablename__ = 'tokens'
    user_id = reference_col('users', nullable=False, ondelete='CASCADE')
    user = relationship('User')

    client_id = reference_col('clients', nullable=False, ondelete='CASCADE')
    client = relationship('Client')

    token_type = Column(db.String(40), nullable=False)

    access_token = Column(db.String(256), nullable=False, unique=True)
    refresh_token = Column(db.String(256), nullable=False, unique=True)

    expires_at = Column(db.DateTime, nullable=False,
                        default=lambda: datetime.utcnow() + timedelta(seconds=3600))

    scopes = Column(db.Text, nullable=False)

    def __init__(self, **kwargs):
        """Create instance."""
        access_token = Token._generate_token()
        refresh_token = Token._generate_token()
        token_type = 'bearer'
        db.Model.__init__(self, access_token=access_token, refresh_token=refresh_token,
                          token_type=token_type, **kwargs)

    @staticmethod
    def _generate_token():
        return getencoder('hex')(urandom(256))[0].decode('utf-8')

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Token({user!r},{client!r})>'.format(user=self.user.email,
                                                     client=self.client.name)
