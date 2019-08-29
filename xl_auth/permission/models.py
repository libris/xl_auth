# -*- coding: utf-8 -*-
"""Permission model."""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

from ..database import Column, Model, SurrogatePK, db, or_, reference_col, relationship


class Permission(SurrogatePK, Model):
    """A permission on a Collection, granted to a User."""

    __table_args__ = (db.UniqueConstraint('user_id', 'collection_id'), SurrogatePK.__table_args__)

    __tablename__ = 'permissions'
    user_id = reference_col('users', nullable=False)
    user = relationship('User', back_populates='permissions', foreign_keys=user_id, lazy='joined')
    collection_id = reference_col('collections', nullable=False)
    collection = relationship('Collection', back_populates='permissions', lazy='joined')

    registrant = Column(db.Boolean(), default=False, nullable=False)
    cataloger = Column(db.Boolean(), default=False, nullable=False)
    cataloging_admin = Column(db.Boolean(), default=False, nullable=False)
    global_registrant = Column(db.Boolean(), default=False, nullable=False)

    modified_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                         nullable=False)
    modified_by_id = reference_col('users', nullable=False)
    modified_by = relationship('User', foreign_keys=modified_by_id)

    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = reference_col('users', nullable=False)
    created_by = relationship('User', foreign_keys=created_by_id)

    @staticmethod
    def get_modified_and_created_by_user(user):
        """Get all permissions created or modified by specified user."""
        return Permission.query.filter(or_(Permission.created_by == user,
                                           Permission.modified_by == user)).all()

    @staticmethod
    def delete_all_by_user(user):
        """Delete all permissions for specified user."""
        Permission.query.filter_by(user=user).delete()

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Permission({user!r}@{collection!r})>'.format(user=self.user,
                                                              collection=self.collection)
