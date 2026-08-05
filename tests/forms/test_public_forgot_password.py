"""Test public ForgotPasswordForm."""


from xl_auth.public.forms import ForgotPasswordForm


# noinspection PyUnusedLocal
def test_validate_unknown_username(db):
    """Unknown username still validates at the form level.

    The form doesn't reveal whether an account exists; that decision (and the
    active-reset limit) is enforced in ``public.views.forgot_password``, which always
    returns the same generic response.
    """
    form = ForgotPasswordForm(username='unknown@example.com')

    assert form.validate() is True


def test_validate_success(user):
    """Validate using the expected field."""
    form = ForgotPasswordForm(username=user.email)

    assert form.validate() is True


# noinspection PyUnusedLocal
def test_validate_requires_username(db):
    """An empty username fails basic field validation."""
    form = ForgotPasswordForm(username='')

    assert form.validate() is False
