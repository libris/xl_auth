# -*- coding: utf-8 -*-
"""Factories to help in tests."""

from __future__ import absolute_import, division, print_function, unicode_literals

from random import choice

from factory import LazyFunction, PostGenerationMethodCall, Sequence
from factory.alchemy import SQLAlchemyModelFactory

from xl_auth.client.models import Client
from xl_auth.collection.models import Collection
from xl_auth.database import db
from xl_auth.grant.models import Grant
from xl_auth.permission.models import Permission
from xl_auth.token.models import Token
from xl_auth.user.models import User


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """User factory."""

    email = Sequence(lambda _: 'user{0}@example.com'.format(_))
    full_name = Sequence(lambda _: 'full_name{0}'.format(_))
    password = PostGenerationMethodCall('set_password', 'example')
    active = True

    class Meta:
        """Factory configuration."""

        model = User


class SuperUserFactory(BaseFactory):
    """Super user factory."""

    email = Sequence(lambda _: 'admin{0}@example.com'.format(_))
    full_name = Sequence(lambda _: 'full_name{0}'.format(_))
    password = PostGenerationMethodCall('set_password', 'example')
    active = True
    is_admin = True

    class Meta:
        """Factory configuration."""

        model = User


class CollectionFactory(BaseFactory):
    """Collection factory."""

    code = Sequence(lambda _: 'c{0}'.format(_))
    friendly_name = Sequence(lambda _: 'friendly_name{0}'.format(_))
    category = choice(['bibliography', 'library', 'uncategorized'])
    active = True

    class Meta:
        """Factory configuration."""

        model = Collection


class PermissionFactory(BaseFactory):
    """Permission factory."""

    user = LazyFunction(UserFactory)
    collection = LazyFunction(CollectionFactory)

    class Meta:
        """Factory configuration."""

        model = Permission


class ClientFactory(BaseFactory):
    """Client factory."""

    name = Sequence(lambda _: 'name{0}'.format(_))
    description = Sequence(lambda _: 'description{0}'.format(_))
    is_confidential = True
    redirect_uris = 'http://example.com'
    default_scopes = 'read write'
    created_by = '1'

    class Meta:
        """Factory configuration."""

        model = Client


class GrantFactory(BaseFactory):
    """Grant factory."""

    user = LazyFunction(UserFactory)
    client = LazyFunction(ClientFactory)

    redirect_uri = 'http://example.com'
    scopes = 'read write'

    class Meta:
        """Factory configuration."""

        model = Grant


class TokenFactory(BaseFactory):
    """Token factory."""

    user = LazyFunction(UserFactory)
    client = LazyFunction(ClientFactory)

    token_type = 'Bearer'
    access_token = Sequence(lambda _: 'accessToken{0}'.format(_))
    refresh_token = Sequence(lambda _: 'refreshToken{0}'.format(_))

    scopes = 'read write'

    class Meta:
        """Factory configuration."""

        model = Token
