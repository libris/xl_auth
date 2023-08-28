"""Test resetting forgotten password."""


from datetime import datetime, timedelta

from flask import current_app, url_for
from flask_babel import gettext as _
from markupsafe import escape

from xl_auth.user.models import PasswordReset

from ..factories import UserFactory


def test_can_complete_password_reset_flow(db, testapp):
    """Successfully request password reset, use code to change password and activate account."""
    inactive_user = UserFactory(is_active=False)
    db.session.commit()
    assert inactive_user.is_active is False
    # Check expected premises.
    user_creator = inactive_user.created_by
    initial_modified_at = inactive_user.modified_at
    initial_modified_by = inactive_user.modified_by
    assert initial_modified_by != inactive_user
    # Goes to homepage.
    res = testapp.get('/')
    # Clicks on 'Forgot password'.
    res = res.click(_('Forgot password?'))
    # Fills out ForgotPasswordForm.
    username_with_different_casing = inactive_user.email.upper()
    form = res.forms['forgotPasswordForm']
    form['username'] = username_with_different_casing
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200

    # New PasswordReset is added to DB.
    password_reset = PasswordReset.query.filter_by(user=inactive_user).first()
    assert password_reset.is_active is True
    assert password_reset.expires_at > (datetime.utcnow() + timedelta(seconds=3600))
    assert password_reset.user.modified_at == initial_modified_at

    # URL sent to user email.
    reset_password_url = url_for('public.reset_password', email=password_reset.user.email,
                                 code=password_reset.code, _external=True)

    # Goes to reset password link.
    res = testapp.get(reset_password_url)
    # Fills out ResetPasswordForm.
    form = res.forms['resetPasswordForm']
    form['confirm'] = form['password'] = 'unicorns are real'
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200

    # PasswordReset no longer active, password update succeeded and user is activated.
    updated_password_reset = PasswordReset.query.filter_by(user=password_reset.user).first()
    assert updated_password_reset.is_active is False
    assert updated_password_reset.user.check_password('unicorns are real') is True
    assert updated_password_reset.user.is_active is True
    # 'modified_by' is updated to reflect change, with 'created_by' intact.
    assert updated_password_reset.user.created_by == user_creator
    assert updated_password_reset.user.modified_at != initial_modified_at
    assert updated_password_reset.user.modified_by == updated_password_reset.user


# noinspection PyUnusedLocal
def test_sees_error_message_if_username_does_not_exist(user, testapp):
    """Show error if username doesn't exist."""
    # Goes to 'Forgot Password?' page.
    res = testapp.get(url_for('public.forgot_password'))
    # Fills out ForgotPasswordForm.
    form = res.forms['forgotPasswordForm']
    form['username'] = 'unknown@example.com'
    # Submits.
    res = form.submit()
    # Sees error.
    assert _('Unknown username/email') in res

    # No PasswordReset is added.
    password_reset = PasswordReset.query.filter_by(user=user).first()
    assert password_reset is None


# noinspection PyUnusedLocal
def test_sees_error_message_if_username_does_not_match_exist(user, password_reset, testapp):
    """Show error if username doesn't match code when resetting."""
    assert user != password_reset.user

    # Goes to reset password link.
    res = testapp.get(url_for('public.reset_password', email=user.email,
                              code=password_reset.code))
    # Fills out ResetPasswordForm.
    form = res.forms['resetPasswordForm']
    form['confirm'] = form['password'] = 'superSecret'
    # Submits.
    res = form.submit()
    # Sees error.
    assert escape(_('Reset code "%(code)s" does not exit', code=password_reset.code)) in res


# noinspection PyUnusedLocal
def test_sees_error_message_if_reset_code_is_expired(password_reset, testapp):
    """Show error if reset code has expired."""
    password_reset.expires_at = datetime.utcnow() - timedelta(seconds=1)
    password_reset.save()
    # Goes to reset password link.
    res = testapp.get(url_for('public.reset_password', email=password_reset.user.email,
                              code=password_reset.code))
    # Fills out ResetPasswordForm.
    form = res.forms['resetPasswordForm']
    form['confirm'] = form['password'] = 'superSecret'
    # Submits.
    res = form.submit()
    # Sees error.
    assert escape(_('Reset code "%(code)s" expired at %(isoformat)s', code=password_reset.code,
                    isoformat=password_reset.expires_at.isoformat() + 'Z')) in res


# noinspection PyUnusedLocal
def test_sees_error_message_if_attempting_to_use_reset_code_twice(password_reset, testapp):
    """Show error if reset code has already been used."""
    # Goes to reset password link.
    res = testapp.get(url_for('public.reset_password', email=password_reset.user.email,
                              code=password_reset.code))
    # Fills out ResetPasswordForm.
    form = res.forms['resetPasswordForm']
    form['confirm'] = form['password'] = 'superSecret'
    # Submits.
    res = form.submit().follow()
    assert res.status_code == 200

    # Does the same thing again.
    res = testapp.get(url_for('public.reset_password', email=password_reset.user.email,
                              code=password_reset.code))
    form = res.forms['resetPasswordForm']
    form['confirm'] = form['password'] = 'superSecret'
    res = form.submit()
    # Sees error.
    assert escape(_('Reset code "%(code)s" already used (%(isoformat)s)', code=password_reset.code,
                    isoformat=password_reset.modified_at.isoformat() + 'Z')) in res


def test_sees_error_message_if_too_many_active_password_resets(user, testapp):
    """Show error if too many active password resets exist."""
    # Create active password resets
    for _i in range(0, current_app.config['XL_AUTH_MAX_ACTIVE_PASSWORD_RESETS']):
        # Goes to homepage.
        res = testapp.get('/')
        # Clicks on 'Forgot password'.
        res = res.click(_('Forgot password?'))
        # Fills out ForgotPasswordForm.
        form = res.forms['forgotPasswordForm']
        form['username'] = user.email
        # Submits.
        res = form.submit().follow()
        assert res.status_code == 200

    active_resets = user.get_active_and_recent_password_resets()
    assert len(active_resets) == current_app.config['XL_AUTH_MAX_ACTIVE_PASSWORD_RESETS']

    # Try to create one additional password reset
    # Goes to homepage.
    res = testapp.get('/')
    # Clicks on 'Forgot password'.
    res = res.click(_('Forgot password?'))
    # Fills out ForgotPasswordForm.
    form = res.forms['forgotPasswordForm']
    form['username'] = user.email
    # Submits.
    res = form.submit()
    assert res.status_code == 200
    assert _('You already have an active password reset. Please check your email inbox (and your '
             'Spam folder) or try again later.') in res
