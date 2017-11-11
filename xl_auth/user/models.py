# -*- coding: utf-8 -*-
"""User models."""

from __future__ import absolute_import, division, print_function, unicode_literals

import hashlib
from binascii import hexlify
from datetime import datetime, timedelta
from os import urandom

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


class PasswordReset(SurrogatePK, Model):
    """Password reset token for a user."""

    __tablename__ = 'password_resets'
    user_id = reference_col('users', nullable=True)
    user = relationship('User', back_populates='password_resets', uselist=False)
    code = Column(db.String(32), unique=True, nullable=False,
                  default=lambda: PasswordReset._get_rand_hex_str(32))
    is_active = Column(db.Boolean(), default=True, nullable=False)
    expires_at = Column(db.DateTime, nullable=False,
                        default=lambda: datetime.utcnow() + timedelta(hours=7 * 24))

    modified_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user, **kwargs):
        """Create instance."""
        db.Model.__init__(self, user=user, **kwargs)

    @staticmethod
    def get_by_email_and_code(email, code):
        """Get by `(email, code)` pair."""
        user = User.get_by_email(email)
        if user:
            return PasswordReset.query.filter_by(code=code, user=user).first()

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<PasswordReset({email!r})>'.format(email=self.user.email)


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = 'users'
    email = Column(db.String(255), unique=True, nullable=False)
    full_name = Column(db.String(255), unique=False, nullable=False)
    password = Column(db.Binary(128), nullable=False)
    active = Column(db.Boolean(), default=False, nullable=False)
    last_login_at = Column(db.DateTime, default=None)
    is_admin = Column(db.Boolean(), default=False, nullable=False)
    permissions = relationship('Permission', back_populates='user')
    roles = relationship('Role', back_populates='user')
    password_resets = relationship('PasswordReset', back_populates='user')

    modified_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, email, full_name, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, email=email, full_name=full_name, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.set_password(hexlify(urandom(16)))

    @staticmethod
    def get_by_email(email):
        """Get by email."""
        return User.query.filter(User.email.ilike(email)).first()

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    def update_last_login(self, commit=True):
        """Set 'last_login_at' to current datetime."""
        self.last_login_at = datetime.utcnow()
        if commit:
            self.save()

    def get_gravatar_url(self, size=32):
        """Get Gravatar URL."""
        hashed_email = hashlib.md5(str(self.email).lower().encode()).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=mm&s={}'.format(hashed_email, size)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({email!r})>'.format(email=self.email)
