"""Test public LoginForm."""


from flask_babel import gettext as _

from xl_auth.public.forms import LoginForm


def test_validate_success(user):
    """Login successful."""
    user.set_password('example')
    user.save()
    form = LoginForm(username=user.email, password='example')
    assert form.validate() is True
    assert form.user == user


def test_validate_success_with_different_username_casing(user):
    """Login successful, but this time with username/email in different casing."""
    user.email = 'me@lowercase-club.se'
    user.set_password('example')
    user.save()
    form = LoginForm(username=user.email.upper(), password='example')
    assert form.validate() is True
    assert form.user == user


def _assert_generic_login_error(form):
    """The failure has a single generic message, form-level (not on a field).

    Form-level means ``flash_errors`` won't prefix it with a field label, and it
    doesn't disclose which of username/password was wrong.
    """
    generic_error = _('The username or password you entered is incorrect.')
    assert generic_error in form.form_errors
    assert generic_error not in form.username.errors
    assert generic_error not in form.password.errors


# noinspection PyUnusedLocal
def test_validate_unknown_username(db):
    """Unknown username yields the generic error (no account enumeration)."""
    form = LoginForm(username='unknown@example.com', password='example')
    assert form.validate() is False
    _assert_generic_login_error(form)
    assert form.user is None


def test_validate_invalid_password(user):
    """Invalid password yields the generic error (indistinguishable from unknown user)."""
    user.set_password('example')
    user.save()
    form = LoginForm(username=user.email, password='wrongPassword')
    assert form.validate() is False
    _assert_generic_login_error(form)


def test_validate_inactive_user(user):
    """Inactive user yields the generic error (does not reveal the account exists)."""
    user.is_active = False
    user.set_password('example')
    user.save()
    # Correct username and password, but user is not activated.
    form = LoginForm(username=user.email, password='example')
    assert form.validate() is False
    _assert_generic_login_error(form)
    # The account's existence must not leak via ``form.user`` either.
    assert form.user is None
