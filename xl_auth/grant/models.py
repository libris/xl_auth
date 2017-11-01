# -*- coding: utf-8 -*-
"""Grant models."""

from __future__ import absolute_import, division, print_function, unicode_literals

from codecs import getencoder
from datetime import datetime, timedelta
from os import urandom

from ..database import Column, Model, SurrogatePK, db, reference_col, relationship


class Grant(SurrogatePK, Model):
    """An OAuth2 Grant token."""

    __tablename__ = 'grants'
    user_id = reference_col('users', nullable=False, ondelete='CASCADE')
    user = relationship('User')

    client_id = reference_col('clients', nullable=False, ondelete='CASCADE')
    client = relationship('Client')

    code = Column(db.String(256), nullable=False)

    redirect_uri = Column(db.String(256), nullable=False)
    expires_at = Column(db.DateTime, nullable=False,
                        default=lambda: datetime.utcnow() + timedelta(seconds=3600))

    scopes = Column(db.Text, nullable=False)

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Grant({user!r},{client!r})>'.format(user=self.user.email,
                                                     client=self.client.name)
