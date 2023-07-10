"""Factories to help in tests."""


from datetime import datetime
from random import choice

from factory import LazyFunction, PostGenerationMethodCall, Sequence
from factory.alchemy import SQLAlchemyModelFactory

from xl_auth.collection.models import Collection
from xl_auth.database import db
from xl_auth.oauth.client.models import Client
from xl_auth.oauth.grant.models import Grant
from xl_auth.oauth.token.models import Token
from xl_auth.permission.models import Permission
from xl_auth.user.models import PasswordReset, User


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class SuperUserFactory(BaseFactory):
    """Super user factory."""

    email = Sequence(lambda _: 'admin{0}@example.com'.format(_))
    full_name = Sequence(lambda _: 'full_name{0}'.format(_))
    password = PostGenerationMethodCall('set_password', 'example')
    is_active = True
    is_admin = True

    tos_approved_at = LazyFunction(datetime.utcnow)

    modified_by_id = '1'
    created_by_id = '1'

    class Meta:
        """Factory configuration."""

        model = User


class UserFactory(BaseFactory):
    """User factory."""

    email = Sequence(lambda _: 'user{0}@example.com'.format(_))
    full_name = Sequence(lambda _: 'full_name{0}'.format(_))
    password = PostGenerationMethodCall('set_password', 'example')
    is_active = True

    tos_approved_at = LazyFunction(datetime.utcnow)

    modified_by = LazyFunction(SuperUserFactory)
    created_by = LazyFunction(SuperUserFactory)

    class Meta:
        """Factory configuration."""

        model = User


class PasswordResetFactory(BaseFactory):
    """PasswordReset factory."""

    user = LazyFunction(UserFactory)

    class Meta:
        """Factory configuration."""

        model = PasswordReset


class CollectionFactory(BaseFactory):
    """Collection factory."""

    code = Sequence(lambda _: 'c{0}'.format(_))
    friendly_name = Sequence(lambda _: 'friendly_name{0}'.format(_))
    category = choice(['bibliography', 'library', 'uncategorized'])
    is_active = True

    modified_by = LazyFunction(UserFactory)
    created_by = LazyFunction(UserFactory)

    class Meta:
        """Factory configuration."""

        model = Collection


class PermissionFactory(BaseFactory):
    """Permission factory."""

    user = LazyFunction(UserFactory)
    collection = LazyFunction(CollectionFactory)

    modified_by = LazyFunction(UserFactory)
    created_by = LazyFunction(UserFactory)

    class Meta:
        """Factory configuration."""

        model = Permission


class ClientFactory(BaseFactory):
    """Client factory."""

    name = Sequence(lambda _: 'name{0}'.format(_))
    description = Sequence(lambda _: 'description{0}'.format(_))
    is_confidential = True
    redirect_uris = 'https://libris.kb.se http://example.com'
    default_scopes = 'read write'

    modified_by = LazyFunction(UserFactory)
    created_by = LazyFunction(UserFactory)

    class Meta:
        """Factory configuration."""

        model = Client


class GrantFactory(BaseFactory):
    """Grant factory."""

    user = LazyFunction(UserFactory)
    client = LazyFunction(ClientFactory)
    code = Sequence(lambda _: 'grantCode{0}'.format(_))

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

    scopes = 'write read'

    class Meta:
        """Factory configuration."""

        model = Token
