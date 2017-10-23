# -*- coding: utf-8 -*-
"""User models."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
import hashlib

from flask_login import UserMixin

from ..database import Column, Model, SurrogatePK, db, reference_col, relationship
from ..extensions import bcrypt


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col('users', nullable=True)
    user = relationship('User', back_populates='roles', uselist=False)

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = 'users'
    email = Column(db.String(255), unique=True, nullable=False)
    full_name = Column(db.String(255), unique=False, nullable=False)
    password = Column(db.Binary(128), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)
    permissions = relationship('Permission', back_populates='user')
    roles = relationship('Role', back_populates='user')
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, email, full_name, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, email=email, full_name=full_name, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    def get_gravatar_url(self, size=32):
        """Get Gravatar URL."""
        hashed_email = hashlib.md5(str(self.email).lower()).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=mm&s={}'.format(hashed_email, size)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({email!r})>'.format(email=self.email)
