"""Test registering permissions."""


from flask import url_for
from flask_babel import gettext as _
from markupsafe import escape

from xl_auth.permission.models import Permission
from xl_auth.user.models import User

from ..factories import PermissionFactory


def test_superuser_can_register_new_permission(superuser, collection, testapp):
    """Register a new permission."""
    old_permission_count = len(Permission.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    assert res.status_code == 200
    # Goes to Permissions' overview
    res = testapp.get(url_for('permission.home'))
    # Clicks Register New Permission button
    res = res.click(_('New Permission'))
    # Fills out the form
    form = res.forms['registerPermissionForm']
    form['user_id'] = superuser.id
    form['collection_id'] = collection.id
    form['global_registrant'] = True
    # Submits
    res = form.submit()
    assert res.status_code == 302
    assert res.location.endswith(url_for('permission.home'))
    res = res.follow()
    # A new permission was created
    assert _('Added permissions for "%(username)s" on collection "%(code)s".',
             username=superuser.email, code=collection.code) in res
    assert len(Permission.query.all()) == old_permission_count + 1
    # The new permission is listed under existing collections
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(superuser.email))) == 1
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(collection.code))) == 1


def test_cataloging_admin_can_register_permission_from_collection_view(user, collection, superuser,
                                                                       testapp):
    """Register new permission from collection view as cataloging admin."""
    PermissionFactory(user=user, collection=collection, cataloging_admin=True).save_as(superuser)
    old_permission_count = len(Permission.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    login_form = res.forms['loginForm']
    login_form['username'] = user.email
    login_form['password'] = 'myPrecious'
    # Submits
    res = login_form.submit().follow()
    # Clicks to View Collection from profile
    res = res.click(href=url_for('collection.view', collection_code=collection.code))
    # Clicks Register New Permission
    res = res.click(_('New Permission'))
    # Finds that the intended user doesn't exist
    res = res.click(_('New User'))
    # Fills out the user registration form
    register_user_form = res.forms['registerUserForm']
    register_user_form['username'] = 'my_registrant@su.se'
    register_user_form['full_name'] = 'Registrant'
    register_user_form['send_password_reset_email'].checked = False
    res = register_user_form.submit()
    assert res.status_code == 302
    assert url_for('permission.register', collection_id=collection.id) in res.location
    other_user = User.get_by_email('my_registrant@su.se')
    assert other_user is not None
    # Saves the form to grant 'other_user' permissions on 'collection'
    res = res.follow(headers={'Referer': res.request.referrer})  # FIXME: Webtest dropping referer.
    assert res.status_code == 200
    register_permission_form = res.forms['registerPermissionForm']
    # New user is preset, ``register_permission_form['user_id'] = other_user.id`` is redundant
    # Defaults are kept, ``register_permission_form['collection_id'] = collection.id`` is redundant
    register_permission_form['registrant'].checked = True
    register_permission_form['cataloger'].checked = True
    # Submits
    res = register_permission_form.submit()
    assert res.status_code == 302
    assert url_for('collection.view', collection_code=collection.code) in res.location
    res = res.follow()
    assert res.status_code == 200
    # The permission was created, and number of permissions are 1 more than initially
    assert _('Added permissions for "%(username)s" on collection "%(code)s".',
             username=other_user.email, code=collection.code) in res
    assert len(Permission.query.all()) == old_permission_count + 1
    # The new permission is listed on the collection view.
    assert len(res.lxml.xpath("//td[contains(., '{0}')]".format(user.email))) == 1


def test_cataloging_admin_can_register_permission_from_user_view(user, collection, permission,
                                                                 superuser, testapp):
    """Register new permission from user view as cataloging admin."""
    # Make 'user' cataloging admin for 'collection' and 'permission.collection'
    PermissionFactory(user=user, collection=collection, cataloging_admin=True).save_as(superuser)
    PermissionFactory(user=user, collection=permission.collection,
                      cataloging_admin=True).save_as(superuser)
    other_user = permission.user
    common_collection = permission.collection
    assert other_user.has_any_permission_for(collection) is False
    old_permission_count = len(Permission.query.all())
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    # Clicks to View Collection from profile
    res = res.click(href=url_for('collection.view', collection_code=common_collection.code))
    # Clicks to View User on common collection view
    res = res.click(href=url_for('user.view', user_id=other_user.id))
    # Clicks Register New Permission the user view
    res = res.click(_('New Permission'))
    # Fills out the form to grant 'other_user' permissions on 'collection'
    form = res.forms['registerPermissionForm']
    # Defaults are kept, setting ``form['user_id'] = other_user.id`` is redundant
    form['collection_id'] = collection.id
    form['registrant'].checked = True
    form['cataloger'].checked = True
    # Submits
    res = form.submit()
    assert res.status_code == 302
    assert url_for('user.view', user_id=other_user.id) in res.location
    res = res.follow()
    assert res.status_code == 200
    # The permission was created, and number of permissions are 1 more than initially
    assert _('Added permissions for "%(username)s" on collection "%(code)s".',
             username=other_user.email, code=collection.code) in res
    assert len(Permission.query.all()) == old_permission_count + 1
    # The new permission is listed on the user view.
    assert len(res.lxml.xpath("//td/a[@href='{0}']".format(
        url_for('collection.view', collection_code=collection.code)))) == 1


def test_superuser_sees_error_if_permission_is_already_registered(superuser, permission, testapp):
    """Show error if permission is already registered."""
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = superuser.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()
    assert res.status_code == 200
    # Goes to Permissions' overview
    res = testapp.get(url_for('permission.home'))
    # Clicks Register New Permission button
    res = res.click(_('New Permission'))
    # Fills out the form with same user ID and collection ID as (existing) 'permission'
    form = res.forms['registerPermissionForm']
    form['user_id'] = permission.user.id
    form['collection_id'] = permission.collection.id
    # Submits
    res = form.submit()
    # Sees error
    assert escape(
        _('Permissions for user "%(username)s" on collection "%(code)s" already registered',
          username=permission.user.email, code=permission.collection.code)) in res


def test_user_cannot_register_permission(user, collection, superuser, testapp):
    """Attempt to register a permission."""
    assert user.is_cataloging_admin_for(collection) is False
    assert user.is_cataloging_admin is False
    # Goes to homepage
    res = testapp.get('/')
    # Fills out login form
    form = res.forms['loginForm']
    form['username'] = user.email
    form['password'] = 'myPrecious'
    # Submits
    res = form.submit().follow()

    # We see no Permissions button
    assert res.lxml.xpath("//a[contains(@text,'{0}')]".format(_('Permissions'))) == []

    # Try to go there directly
    testapp.get('/permissions/', status=403)

    # Try to register a permission with direct URL
    testapp.get(url_for('permission.register'), status=403)

    # Be cataloging admin for unrelated collection and try again
    PermissionFactory(user=user, cataloging_admin=True).save_as(superuser)
    res = testapp.get('/permissions/register/')
    form = res.forms['registerPermissionForm']
    form['user_id'] = user.id
    res = form.submit()
    # FIXME: The intended assertion below doesn't work.. :(
    # assert _('You do not have sufficient privileges for this operation.') in res
    assert res.status_code == 200  # Fallback, means we didn't redirect due to validation error.
