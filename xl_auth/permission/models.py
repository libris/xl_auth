# -*- coding: utf-8 -*-
"""Permission model."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

from ..database import Column, Model, SurrogatePK, db, reference_col, relationship


class Permission(SurrogatePK, Model):
    """A permission on a Collection, granted to a User."""

    __table_args__ = (db.UniqueConstraint('user_id', 'collection_id'), SurrogatePK.__table_args__)

    __tablename__ = 'permissions'
    user_id = reference_col('users', nullable=False)
    user = relationship('User', back_populates='permissions', foreign_keys=user_id)
    collection_id = reference_col('collections', nullable=False)
    collection = relationship('Collection', back_populates='permissions')

    registrant = Column(db.Boolean(), default=False, nullable=False)
    cataloger = Column(db.Boolean(), default=False, nullable=False)
    cataloging_admin = Column(db.Boolean(), default=False, nullable=False)

    modified_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                         nullable=False)
    modified_by_id = reference_col('users', nullable=False)
    modified_by = relationship('User', foreign_keys=modified_by_id)

    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = reference_col('users', nullable=False)
    created_by = relationship('User', foreign_keys=created_by_id)

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Permission({user!r}@{collection!r})>'.format(user=self.user,
                                                              collection=self.collection)
