"""Test permission RegisterForm."""

from __future__ import absolute_import, division, print_function, unicode_literals

from flask_babel import gettext as _

from xl_auth.permission.forms import RegisterForm

from ..factories import PermissionFactory, UserFactory


def test_validate_with_placeholder_user_id(superuser, collection):
    """Attempt registering entry with the placeholder ID."""
    form = RegisterForm(superuser, user_id='-1', collection_id=collection.id)

    assert form.validate() is False
    assert _('A user must be selected.') in form.user_id.errors


def test_validate_without_user_id(superuser, collection):
    """Attempt registering entry with empty string for user ID."""
    form = RegisterForm(superuser, user_id='', collection_id=collection.id)

    assert form.validate() is False
    assert _('This field is required.') in form.user_id.errors


def test_validate_with_placeholder_collection_id(superuser, user):
    """Attempt registering entry with the placeholder ID."""
    form = RegisterForm(superuser, user_id=user.id, collection_id='-1')

    assert form.validate() is False
    assert _('A collection must be selected.') in form.collection_id.errors


def test_validate_without_collection_id(superuser, user):
    """Attempt registering entry with empty string for collection ID."""
    form = RegisterForm(superuser, user_id=user.id, collection_id='')

    assert form.validate() is False
    assert _('This field is required.') in form.collection_id.errors


def test_validate_permission_already_registered(superuser, permission):
    """Attempt registering a (user_id, collection_id) mapping that is already registered."""
    form = RegisterForm(superuser, user_id=permission.user.id,
                        collection_id=permission.collection.id)

    assert form.validate() is False
    assert _('Permissions for user "%(username)s" on collection "%(code)s" already registered',
             username=permission.user.email, code=permission.collection.code
             ) in form.user_id.errors


def test_validate_user_id_does_not_exist(superuser, user, collection):
    """Attempt registering a (user_id, collection_id) mapping where the user ID does not exist."""
    invalid_user_id = user.id + 500
    form = RegisterForm(superuser, user_id=invalid_user_id, collection_id=collection.id)

    assert form.validate() is False
    assert _('User ID "%(user_id)s" does not exist',
             user_id=invalid_user_id) in form.user_id.errors


def test_validate_collection_id_does_not_exist(superuser, user, collection):
    """Attempt registering a (user_id, collection_id) mapping where collection does not exist."""
    invalid_collection_id = collection.id + 500
    form = RegisterForm(superuser, user_id=user.id, collection_id=invalid_collection_id)

    assert form.validate() is False
    assert _('Collection ID "%(collection_id)s" does not exist',
             collection_id=invalid_collection_id) in form.collection_id.errors


def test_validate_register_permission_as_user(user, collection):
    """Attempt registering permission as a user that's not cataloging admin."""
    form = RegisterForm(user, user_id=user.id, collection_id=collection.id, registrant=True,
                        cataloger=False, cataloging_admin=False)

    form.validate()
    assert _('You do not have sufficient privileges for this operation.') in \
        form.collection_id.errors


def test_validate_add_cataloging_admin_permission_as_cataloging_admin(user, collection, superuser):
    """Attempt to make another user cataloging admin being only cataloging admin yourself."""
    PermissionFactory(user=user, collection=collection, cataloging_admin=True).save_as(superuser)
    assert user.is_cataloging_admin_for(collection) is True
    other_user = UserFactory().save_as(user)
    form = RegisterForm(user, user_id=other_user.id, collection_id=collection.id,
                        cataloging_admin=True)

    assert form.validate() is True


def test_validate_success_as_cataloging_admin(user, collection, superuser):
    """Register new permission with success as cataloging admin."""
    PermissionFactory(user=user, collection=collection, cataloging_admin=True).save_as(superuser)
    assert user.is_cataloging_admin_for(collection) is True
    other_user = UserFactory().save_as(user)
    form = RegisterForm(user,
                        user_id=other_user.id,
                        collection_id=collection.id,
                        registrant=True,
                        cataloger=True,
                        cataloging_admin=False)

    assert form.validate() is True
    assert form.data == {
        'user_id': other_user.id,
        'collection_id': collection.id,
        'registrant': True,
        'cataloger': True,
        'cataloging_admin': False,
        'next_redirect': None,
        'global_registrant': False
    }


def test_cataloging_admin_cannot_set_global_registrant(user, collection, superuser):
    """Try to manipulate the form and add global_registrant as cataloging admin."""
    PermissionFactory(user=user, collection=collection, cataloging_admin=True).save_as(superuser)
    assert user.is_cataloging_admin_for(collection) is True
    other_user = UserFactory().save_as(user)
    form = RegisterForm(user,
                        user_id=other_user.id,
                        collection_id=collection.id,
                        global_registrant=True)

    assert form.validate() is False


def test_validate_success_as_superuser(superuser, user, collection):
    """Register new permission with success as superuser."""
    form = RegisterForm(superuser,
                        user_id=user.id,
                        collection_id=collection.id,
                        registrant=True,
                        cataloger=True,
                        cataloging_admin=True,
                        global_registrant=True)

    assert form.validate() is True
    assert form.data == {
        'user_id': user.id,
        'collection_id': collection.id,
        'registrant': True,
        'cataloger': True,
        'cataloging_admin': True,
        'global_registrant': True,
        'next_redirect': None
    }
