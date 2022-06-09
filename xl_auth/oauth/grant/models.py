# -*- coding: utf-8 -*-
"""OAuth Grant models."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime, timedelta

from six import string_types
from sqlalchemy import desc
from sqlalchemy.ext.hybrid import hybrid_property

from ...database import Column, Model, SurrogatePK, db, reference_col, relationship

from flask_babel import lazy_gettext as _

class Grant(SurrogatePK, Model):
    """An OAuth2 Grant token."""

    __tablename__ = 'grants'
    user_id = reference_col('users', nullable=False, ondelete='CASCADE')
    user = relationship('User')

    client_id = reference_col('clients', pk_name='client_id', nullable=False, ondelete='CASCADE')
    client = relationship('Client')

    code = Column(db.String(256), nullable=False)

    redirect_uri = Column(db.String(256), nullable=False)
    expires_at = Column(db.DateTime, nullable=False,
                        default=lambda: datetime.utcnow() + timedelta(seconds=3600))

    _scopes = Column(db.Text, nullable=False)

    def __init__(self, scopes=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)
        self.scopes = scopes

    @staticmethod
    def get_all_by_user(user):
        """Get all grants for specified user."""
        return Grant.query.filter_by(user=user).order_by(desc('expires_at')).all()

    @staticmethod
    def delete_all_by_user(user):
        """Delete all grants for specified user."""
        Grant.query.filter_by(user=user).delete()

    @hybrid_property
    def scopes(self):
        """Return scopes list."""
        return self._scopes.split(' ')

    @scopes.setter
    def scopes(self, value):
        """Store scopes list as string."""
        if isinstance(value, string_types):
            self._scopes = value
        elif isinstance(value, list):
            self._scopes = ' '.join(value)
        else:
            self._scopes = value

    @property
    def display_value(self):
        return f"{self.user.email}: {_('Client').lower()} {self.client.name}, {_('Expires At').lower()} {self.client.expires_at}"

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Grant({user!r},{client!r})>'.format(user=self.user.email,
                                                     client=self.client.name)
