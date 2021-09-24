"""Make refresh token optional.

Revision ID: a6c5437cfd80
Revises: 55513723546e
Create Date: 2018-03-27 09:13:01.142853

"""

from __future__ import absolute_import, division, print_function, unicode_literals

from binascii import hexlify
from codecs import getencoder
from datetime import datetime, timedelta
from os import urandom

import sqlalchemy as sa
from alembic import op
from flask_login import UserMixin
from six import string_types
from sqlalchemy import (LargeBinary, Boolean, Column, DateTime, ForeignKey, Integer, String, Text,
                        UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, sessionmaker

# Revision identifiers, used by Alembic.
revision = 'a6c5437cfd80'
down_revision = '55513723546e'
branch_labels = None
depends_on = None

try:
    # noinspection PyCompatibility,PyUnresolvedReferences,PyUnboundLocalVariable
    basestring  # py2
except NameError:
    # noinspection PyShadowingBuiltins
    basestring = str  # py3

Session = sessionmaker()
Base = declarative_base()


def upgrade():
    """Make refresh token field nullable."""
    with op.batch_alter_table('tokens', schema=None) as batch_op:
        batch_op.alter_column('refresh_token',
                              existing_type=sa.VARCHAR(length=256),
                              nullable=True)


def downgrade():
    """Make refresh token field not nullable."""
    bind = op.get_bind()
    session = Session(bind=bind)

    class CRUDMixin(object):
        """Mixin that adds convenience methods for CRUD (create, read, update, delete) ops."""

        @classmethod
        def create_as(cls, current_user, **kwargs):
            """Create a new record and save it to the database as 'current_user'."""
            assert hasattr(cls, 'modified_by') and hasattr(cls, 'created_by')
            instance = cls(**kwargs)
            return instance.save_as(current_user)

        @classmethod
        def create(cls, **kwargs):
            """Create a new record and save it to the database."""
            instance = cls(**kwargs)
            return instance.save()

        def update_as(self, current_user, commit=True, preserve_modified=False, **kwargs):
            """Update specific fields of the record and save as 'current_user'."""
            for attr, value in kwargs.items():
                setattr(self, attr, value)
            return self.save_as(current_user, commit=commit, preserve_modified=preserve_modified)

        def update(self, commit=True, preserve_modified=False, **kwargs):
            """Update specific fields of a record."""
            for attr, value in kwargs.items():
                setattr(self, attr, value)
            return self.save(commit=commit, preserve_modified=preserve_modified)

        def save_as(self, current_user, commit=True, preserve_modified=False):
            """Save instance as 'current_user'."""
            assert hasattr(self, 'modified_by') and hasattr(self, 'created_by')
            # noinspection PyUnresolvedReferences
            if current_user and not self.created_at:
                # noinspection PyAttributeOutsideInit
                self.created_by = current_user
            if current_user and not preserve_modified:
                # noinspection PyAttributeOutsideInit
                self.modified_by = current_user
            return self.save(commit=commit, preserve_modified=preserve_modified)

        def save(self, commit=True, preserve_modified=False):
            """Save the record."""
            session.add(self)
            if commit:
                if preserve_modified and hasattr(self, 'modified_at'):
                    modified_dt = self.modified_at
                    session.commit()
                    self.modified_at = modified_dt
                session.commit()
            return self

        def delete(self, commit=True):
            """Remove the record from the database."""
            session.delete(self)
            return commit and session.commit()

    class Model(CRUDMixin, Base):
        """Base model class that includes CRUD convenience methods."""

        __abstract__ = True

        @staticmethod
        def _get_rand_hex_str(length=32):
            """Create random hex string."""
            return getencoder('hex')(urandom(length // 2))[0].decode('utf-8')

    class SurrogatePK(object):
        """A mixin that adds a surrogate integer primary key column to declarative-mapped class."""

        __table_args__ = {'extend_existing': True}

        id = Column(Integer, primary_key=True)

        @classmethod
        def get_by_id(cls, record_id):
            """Get record by ID."""
            if any((isinstance(record_id, basestring) and record_id.isdigit(),
                    isinstance(record_id, (int, float))),):
                # noinspection PyUnresolvedReferences
                return cls.query.get(int(record_id))
            else:
                return None

    def reference_col(tablename, nullable=False, pk_name='id', ondelete=None, **kwargs):
        """Column that adds primary key foreign key reference.

        Usage ::

            category_id = reference_col('category')
            category = relationship('Category', backref='categories')

        """
        return Column(
            ForeignKey('{0}.{1}'.format(tablename, pk_name), ondelete=ondelete),
            nullable=nullable, **kwargs)

    class Client(Model):
        """An OAuth2 Client."""

        __tablename__ = 'clients'
        client_id = Column(String(32), primary_key=True)
        client_secret = Column(String(256), unique=True, nullable=False)

        is_confidential = Column(Boolean(), default=True, nullable=False)

        _redirect_uris = Column(Text(), nullable=False)
        _default_scopes = Column(Text(), nullable=False)

        # Human readable info fields
        name = Column(String(64), nullable=False)
        description = Column(String(400), nullable=False)

        modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                             nullable=False)
        modified_by_id = reference_col('users', nullable=False)
        modified_by = relationship('User', foreign_keys=modified_by_id)

        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        created_by_id = reference_col('users', nullable=False)
        created_by = relationship('User', foreign_keys=created_by_id)

        def __init__(self, redirect_uris=None, default_scopes=None, **kwargs):
            """Create instance."""
            client_id = Client._get_rand_hex_str(32)
            client_secret = Client._get_rand_hex_str(256)
            Model.__init__(self, client_id=client_id, client_secret=client_secret, **kwargs)
            self.redirect_uris = redirect_uris
            self.default_scopes = default_scopes

        def __repr__(self):
            """Represent instance as a unique string."""
            return '<Client({name!r})>'.format(name=self.name)

    class Collection(SurrogatePK, Model):
        """A collection of library stuff, a.k.a. 'a sigel'."""

        __tablename__ = 'collections'
        code = Column(String(255), unique=True, nullable=False)
        friendly_name = Column(String(255), unique=False, nullable=False)
        category = Column(String(255), nullable=False)
        is_active = Column(Boolean(), default=True)
        permissions = relationship('Permission', back_populates='collection', lazy='joined')
        replaces = Column(String(255))
        replaced_by = Column(String(255))

        modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                             nullable=False)
        modified_by_id = reference_col('users', nullable=False)
        modified_by = relationship('User', foreign_keys=modified_by_id)

        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        created_by_id = reference_col('users', nullable=False)
        created_by = relationship('User', foreign_keys=created_by_id)

        def __init__(self, code, friendly_name, category, **kwargs):
            """Create instance."""
            Model.__init__(self, code=code, friendly_name=friendly_name, category=category,
                           **kwargs)

        def __repr__(self):
            """Represent instance as a unique string."""
            return '<Collection({code!r})>'.format(code=self.code)

    class Role(SurrogatePK, Model):
        """A role for a user."""

        __tablename__ = 'roles'
        name = Column(String(80), unique=True, nullable=False)
        user_id = reference_col('users', nullable=True)
        user = relationship('User', back_populates='roles')

        def __init__(self, name, **kwargs):
            """Create instance."""
            Model.__init__(self, name=name, **kwargs)

        def __repr__(self):
            """Represent instance as a unique string."""
            return '<Role({name})>'.format(name=self.name)

    class PasswordReset(SurrogatePK, Model):
        """Password reset token for a user."""

        __tablename__ = 'password_resets'
        user_id = reference_col('users', nullable=True)
        user = relationship('User', back_populates='password_resets')
        code = Column(String(32), unique=True, nullable=False)
        is_active = Column(Boolean(), default=True, nullable=False)
        expires_at = Column(DateTime, nullable=False,
                            default=lambda: datetime.utcnow() + timedelta(hours=7 * 24))

        modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

        def __init__(self, user, **kwargs):
            """Create instance."""
            Model.__init__(self, user=user, code=self._get_rand_hex_str(32), **kwargs)

        def __repr__(self):
            """Represent instance as a unique string."""
            return '<PasswordReset({email!r})>'.format(email=self.user.email)

    class User(UserMixin, SurrogatePK, Model):
        """A user of the app."""

        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        email = Column(String(255), unique=True, nullable=False)
        full_name = Column(String(255), unique=False, nullable=False)
        password = Column(LargeBinary(128), nullable=False)
        last_login_at = Column(DateTime, default=None)
        tos_approved_at = Column(DateTime, default=None)
        is_active = Column(Boolean(), default=False, nullable=False)
        is_admin = Column(Boolean(), default=False, nullable=False)
        permissions = relationship('Permission', back_populates='user',
                                   foreign_keys='Permission.user_id', lazy='joined')
        roles = relationship('Role', back_populates='user')
        password_resets = relationship('PasswordReset', back_populates='user')

        modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                             nullable=False)
        modified_by_id = reference_col('users', nullable=False)
        modified_by = relationship('User', remote_side=id, foreign_keys=modified_by_id)

        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        created_by_id = reference_col('users', nullable=False)
        created_by = relationship('User', remote_side=id, foreign_keys=created_by_id)

        def __init__(self, email, full_name, password=None, **kwargs):
            """Create instance."""
            Model.__init__(self, email=email, full_name=full_name, **kwargs)
            if password:
                self.set_password(password)
            else:
                self.set_password(hexlify(urandom(16)))

        def __repr__(self):
            """Represent instance as a unique string."""
            return '<User({email!r})>'.format(email=self.email)

    class Permission(SurrogatePK, Model):
        """A permission on a Collection, granted to a User."""

        __table_args__ = (UniqueConstraint('user_id', 'collection_id'), SurrogatePK.__table_args__)

        __tablename__ = 'permissions'
        user_id = reference_col('users', nullable=False)
        user = relationship('User', back_populates='permissions',
                            foreign_keys=user_id, lazy='joined')
        collection_id = reference_col('collections', nullable=False)
        collection = relationship('Collection', back_populates='permissions', lazy='joined')

        registrant = Column(Boolean(), default=False, nullable=False)
        cataloger = Column(Boolean(), default=False, nullable=False)
        cataloging_admin = Column(Boolean(), default=False, nullable=False)

        modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                             nullable=False)
        modified_by_id = reference_col('users', nullable=False)
        modified_by = relationship('User', foreign_keys=modified_by_id)

        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        created_by_id = reference_col('users', nullable=False)
        created_by = relationship('User', foreign_keys=created_by_id)

        def __init__(self, **kwargs):
            """Create instance."""
            Model.__init__(self, **kwargs)

        def __repr__(self):
            """Represent instance as a unique string."""
            return '<Permission({user!r}@{collection!r})>'.format(user=self.user,
                                                                  collection=self.collection)

    class Token(SurrogatePK, Model):
        """An OAuth2 Bearer token."""

        __tablename__ = 'tokens'
        user_id = reference_col('users', nullable=False, ondelete='CASCADE')
        user = relationship('User')

        client_id = reference_col('clients', pk_name='client_id',
                                  nullable=False, ondelete='CASCADE')
        client = relationship('Client')

        token_type = Column(String(40), nullable=False, default='Bearer')

        access_token = Column(String(256), nullable=False, unique=True)
        refresh_token = Column(String(256), unique=True)

        expires_at = Column(DateTime, nullable=False,
                            default=lambda: datetime.utcnow() + timedelta(seconds=3600))

        _scopes = Column(Text, nullable=False)

        def __init__(self, scopes=None, **kwargs):
            """Create instance."""
            Model.__init__(self, **kwargs)
            self.scopes = scopes

        @staticmethod
        def get_all_by_user(user):
            """Get all tokens for specified user."""
            return Token.query.filter_by(user=user).all()

        @staticmethod
        def delete_all_by_user(user):
            """Delete all tokens for specified user."""
            Token.query.filter_by(user=user).delete()

        @hybrid_property
        def expires(self):
            """Return 'expires_at'."""
            return self.expires_at

        @hybrid_property
        def is_active(self):
            """Return still active (now < expires_at)."""
            return self.expires_at > datetime.utcnow()

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

        def __repr__(self):
            """Represent instance as a unique string."""
            return '<Token({user!r},{client!r})>'.format(user=self.user.email,
                                                         client=self.client.name)

    # ensure all tokens have a refresh_token
    for token in session.query(Token).filter(Token.refresh_token == None).all():  # noqa: E711
        token.refresh_token = Model._get_rand_hex_str()
        token.save(commit=True, preserve_modified=True)

    with op.batch_alter_table('tokens', schema=None) as batch_op:
        batch_op.alter_column('refresh_token',
                              existing_type=sa.VARCHAR(length=256),
                              nullable=False)
