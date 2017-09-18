# -*- coding: utf-8 -*-
"""User models."""

from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt

from ..database import Column, Model, SurrogatePK, db


class Collection(SurrogatePK, Model):
    """A collection of library stuff, a.k.a. 'a sigel'."""

    __tablename__ = 'collections'
    code = Column(db.String(255), unique=True, nullable=False)
    friendly_name = Column(db.String(255), unique=False, nullable=False)
    category = Column(db.String(255), nullable=False)
    active = Column(db.Boolean(), default=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    def __init__(self, code, friendly_name, category, **kwargs):
        """Create instance."""
        db.Model.__init__(self, code=code, friendly_name=friendly_name, category=category,
                          **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Collection({code!r})>'.format(code=self.code)
