# -*- coding: utf-8 -*-
"""Factories to help in tests."""

from __future__ import absolute_import, division, print_function, unicode_literals

from factory import PostGenerationMethodCall, Sequence
from factory.alchemy import SQLAlchemyModelFactory

from xl_auth.database import db
from xl_auth.user.models import User


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """User factory."""

    username = Sequence(lambda _: 'user{0}'.format(_))
    email = Sequence(lambda _: 'user{0}@example.com'.format(_))
    password = PostGenerationMethodCall('set_password', 'example')
    active = True

    class Meta:
        """Factory configuration."""

        model = User
