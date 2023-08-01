"""Add modified_by/created_by fields for traceability + make sure libris@kb.se admin user exists.

Revision ID: b984311d26d7
Revises: 072487c42d98
Create Date: 2017-11-21 15:50:10.745763

"""


from binascii import hexlify
from codecs import getencoder
from datetime import datetime
from os import urandom

import sqlalchemy as sa
from alembic import op
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from six import string_types
from sqlalchemy import (LargeBinary, Boolean, Column, DateTime, ForeignKey, Integer, String, Text,
                        UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, sessionmaker

# Revision identifiers, used by Alembic.
revision = 'b984311d26d7'
down_revision = '072487c42d98'
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
    """Add 'modified_by'/'created_by' cols and backfill clients/collections/users/permissions."""
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
                    # noinspection PyAttributeOutsideInit
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
                    isinstance(record_id, (int, float))), ):
                # noinspection PyUnresolvedReferences
                return session.query(cls).get(int(record_id))
            else:
                return None

    def reference_col(tablename, nullable=False, pk_name='id', ondelete=None, **kwargs):
        """Column that adds primary key foreign key reference.

        Usage ::

            category_id = reference_col('category')
            category = relationship('Category', backref='categories')

        """
        return Column(ForeignKey('{0}.{1}'.format(tablename, pk_name), ondelete=ondelete),
                      nullable=nullable, **kwargs)

    class User(UserMixin, SurrogatePK, Model):
        """A user of the app."""

        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        email = Column(String(255), unique=True, nullable=False)
        full_name = Column(String(255), unique=False, nullable=False)
        password = Column(LargeBinary(128), nullable=False)
        last_login_at = Column(DateTime, default=None)
        is_active = Column(Boolean(), default=False, nullable=False)
        is_admin = Column(Boolean(), default=False, nullable=False)
        permissions = relationship('Permission', back_populates='user',
                                   foreign_keys='Permission.user_id')

        modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                             nullable=False)
        modified_by_id = reference_col('users', nullable=True)
        modified_by = relationship('User', remote_side=id, foreign_keys=modified_by_id)

        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        created_by_id = reference_col('users', nullable=True)
        created_by = relationship('User', remote_side=id, foreign_keys=created_by_id)

        def __init__(self, email, full_name, password=None, **kwargs):
            """Create instance."""
            # noinspection PyArgumentList
            super(User, self).__init__(email=email, full_name=full_name, **kwargs)
            if password:
                self.set_password(password)
            else:
                self.set_password(hexlify(urandom(16)))

        @staticmethod
        def get_by_email(email):
            """Get by email."""
            return session.query(User).filter(User.email.ilike(email)).first()

        def set_password(self, password):
            """Set password."""
            self.password = Bcrypt().generate_password_hash(password)

        def save_as(self, current_user, commit=True, preserve_modified=False):
            """Save instance as 'current_user'."""
            if current_user and not self.created_at:
                self.created_by = current_user
            if current_user and not preserve_modified:
                self.modified_by_id = current_user.id
                # Using ``self.modified_by = current_user`` yields error when user modifies itself:
                # "sqlalchemy.exc.CircularDependencyError: Circular dependency detected."
            return self.save(commit=commit, preserve_modified=preserve_modified)

    class Permission(SurrogatePK, Model):
        """A permission on a Collection, granted to a User."""

        __table_args__ = (UniqueConstraint('user_id', 'collection_id'), SurrogatePK.__table_args__)

        __tablename__ = 'permissions'
        user_id = reference_col('users', nullable=False)
        user = relationship('User', back_populates='permissions', foreign_keys=user_id)
        collection_id = reference_col('collections', nullable=False)
        collection = relationship('Collection', back_populates='permissions')

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
            # noinspection PyArgumentList
            super(Permission, self).__init__(**kwargs)

    class Collection(SurrogatePK, Model):
        """A collection of library stuff, a.k.a. 'a sigel'."""

        __tablename__ = 'collections'
        code = Column(String(255), unique=True, nullable=False)
        friendly_name = Column(String(255), unique=False, nullable=False)
        category = Column(String(255), nullable=False)
        is_active = Column(Boolean(), default=True)
        permissions = relationship('Permission', back_populates='collection')
        replaces = Column(String(255))
        replaced_by = Column(String(255))

        modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                             nullable=True)
        modified_by_id = reference_col('users', nullable=True)
        modified_by = relationship('User', foreign_keys=modified_by_id)

        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        created_by_id = reference_col('users', nullable=True)
        created_by = relationship('User', foreign_keys=created_by_id)

        def __init__(self, code, friendly_name, category, **kwargs):
            """Create instance."""
            # noinspection PyArgumentList
            super(Collection, self).__init__(code=code, friendly_name=friendly_name,
                                             category=category, **kwargs)

    class Client(Model):
        """An OAuth2 Client."""

        __tablename__ = 'clients'
        client_id = Column(String(32), primary_key=True)
        client_secret = Column(String(256), unique=True, nullable=False)

        is_confidential = Column(Boolean(), default=True, nullable=False)

        _redirect_uris = Column(Text(), nullable=False)
        _default_scopes = Column(Text(), nullable=False)

        # Human readable info fields
        name = Column(String(64), nullable=True)
        description = Column(String(400), nullable=True)

        modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                             nullable=True)
        modified_by_id = reference_col('users', nullable=True)
        modified_by = relationship('User', foreign_keys=modified_by_id)

        created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
        created_by_id = reference_col('users', nullable=True)
        created_by = relationship('User', foreign_keys=created_by_id)

        def __init__(self, redirect_uris=None, default_scopes=None, **kwargs):
            """Create instance."""
            client_id = Client._get_rand_hex_str(32)
            client_secret = Client._get_rand_hex_str(256)
            # noinspection PyArgumentList
            super(Client, self).__init__(client_id=client_id, client_secret=client_secret,
                                         **kwargs)
            self.redirect_uris = redirect_uris
            self.default_scopes = default_scopes

        @classmethod
        def get_by_id(cls, record_id):
            """Get record by ID."""
            return session.query(Client).filter_by(client_id=record_id).first()

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

    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.alter_column('created_by', new_column_name='created_by_id')
        batch_op.add_column(sa.Column('modified_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('clients_modified_by_id_fkey', 'users',
                                    ['modified_by_id'], ['id'])
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('modified_at', sa.DateTime(), nullable=True))

    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('collections_created_by_id_fkey', 'users',
                                    ['created_by_id'], ['id'])
        batch_op.add_column(sa.Column('modified_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('collections_modified_by_id_fkey', 'users',
                                    ['modified_by_id'], ['id'])

    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('permissions_created_by_id_fkey', 'users',
                                    ['created_by_id'], ['id'])
        batch_op.add_column(sa.Column('modified_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('permissions_modified_by_id_fkey', 'users',
                                    ['modified_by_id'], ['id'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('users_created_by_id_fkey', 'users',
                                    ['created_by_id'], ['id'])
        batch_op.add_column(sa.Column('modified_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('users_modified_by_id_fkey', 'users',
                                    ['modified_by_id'], ['id'])

    # Assert admin user 'libris@kb.se' exists.
    admin_email = 'libris@kb.se'
    superuser = User.get_by_email(admin_email)
    if superuser:
        if not all([superuser.is_active, superuser.is_admin]):
            superuser.is_active = True
            superuser.is_admin = True
            superuser.save()
    else:
        superuser = User(admin_email, 'SuperAdmin', is_active=True, is_admin=True).save()
    superuser.created_by_id = superuser.id
    superuser.modified_by_id = superuser.id
    superuser.save(preserve_modified=True)

    # Backfill 'modified_by' and 'created_by' fields.
    for client in session.query(Client).all():
        client.created_at = datetime.utcnow()
        client.save_as(superuser)

    for collection in session.query(Collection).all():
        collection.created_by = superuser
        collection.modified_by = superuser
        if not collection.modified_at:
            collection.modified_at = collection.created_at
        if collection.modified_at == collection.created_at:
            if collection.replaced_by:
                replacement = session.query(Collection).filter_by(
                    code=collection.replaced_by).first()
                if replacement.created_at > collection.modified_at:
                    collection.modified_at = replacement.created_at
        collection.save_as(superuser, preserve_modified=True)

    for permission in session.query(Permission).all():
        permission.created_by = superuser
        permission.modified_by = superuser
        if not permission.modified_at:
            permission.modified_at = permission.created_at
        permission.save_as(superuser, preserve_modified=True)

    for user in session.query(User).all():
        user.created_by_id = superuser.id
        user.modified_by_id = superuser.id
        if not user.modified_at:
            user.modified_at = user.created_at
        user.save_as(superuser, preserve_modified=True)

    # Strictify NOT NULL constraints.
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('created_at', existing_type=sa.DateTime(), nullable=False)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=False)

        batch_op.alter_column('name', existing_type=sa.String(length=64), nullable=False)
        batch_op.alter_column('description', existing_type=sa.String(length=400), nullable=False)

    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=False)

    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=False)


def downgrade():
    """Drop 'modified_by'/'created_by' cols and 'laxify NOT NULL constraints."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=True)

    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=True)

    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=True)

    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.alter_column('description', existing_type=sa.String(length=400), nullable=True)
        batch_op.alter_column('name', existing_type=sa.String(length=64), nullable=True)
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.alter_column('created_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=True)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('users_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.drop_constraint('users_created_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.drop_constraint('permissions_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.drop_constraint('permissions_created_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.drop_constraint('collections_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.drop_constraint('collections_created_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.drop_column('modified_at')
        batch_op.drop_column('created_at')
        batch_op.drop_constraint('clients_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.alter_column('created_by_id', new_column_name='created_by')
