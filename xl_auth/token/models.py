# -*- coding: utf-8 -*-
"""Token models."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta

from ..database import Column, Model, SurrogatePK, db, reference_col, relationship


class Token(SurrogatePK, Model):
    """An OAuth2 Bearer token."""

    __tablename__ = 'tokens'
    user_id = reference_col('users', nullable=False, ondelete='CASCADE')
    user = relationship('User')

    client_id = reference_col('clients', nullable=False, ondelete='CASCADE')
    client = relationship('Client')

    token_type = Column(db.String(40), nullable=False, default='Bearer')

    access_token = Column(db.String(256), nullable=False, unique=True)
    refresh_token = Column(db.String(256), nullable=False, unique=True)

    expires_at = Column(db.DateTime, nullable=False,
                        default=lambda: datetime.utcnow() + timedelta(seconds=3600))

    scopes = Column(db.Text, nullable=False)

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Token({user!r},{client!r})>'.format(user=self.user.email,
                                                     client=self.client.name)
