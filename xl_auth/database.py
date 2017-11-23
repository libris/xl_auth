# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related utilities."""

from __future__ import absolute_import, division, print_function, unicode_literals

from codecs import getencoder
from os import urandom

from .extensions import db

try:
    # noinspection PyCompatibility,PyUnresolvedReferences,PyUnboundLocalVariable
    basestring  # py2
except NameError:
    # noinspection PyShadowingBuiltins
    basestring = str  # py3

# Alias common SQLAlchemy names.
Column = db.Column
relationship = db.relationship


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

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
        db.session.add(self)
        if commit:
            if preserve_modified and hasattr(self, 'modified_at'):
                modified_dt = self.modified_at
                db.session.commit()
                self.modified_at = modified_dt
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True

    @staticmethod
    def _get_rand_hex_str(length=32):
        """Create random hex string."""
        return getencoder('hex')(urandom(length // 2))[0].decode('utf-8')


# From Mike Bayer's "Building the app" talk https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer primary key column to any declarative-mapped class."""

    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

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
    return db.Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name), ondelete=ondelete),
        nullable=nullable, **kwargs)
