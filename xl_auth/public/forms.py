"""Public forms."""


from datetime import datetime

from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField
from wtforms.validators import DataRequired, EqualTo, Length

from ..extensions import bcrypt
from ..user.models import PasswordReset, User

_TIMING_EQUALIZER_HASH = bcrypt.generate_password_hash('timing-equalizer')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(_('Username'), validators=[DataRequired()])
    password = PasswordField(_('Password'), validators=[DataRequired()])
    next_redirect = HiddenField()

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, extra_validators=None):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate(extra_validators)
        if not initial_validation:
            return False

        # Generic message for each kind of failure (unknown user, invalid password,
        # inactive/deleted account) to prevent user enumeration.
        generic_error = _('The username or password you entered is incorrect.')

        self.user = User.get_by_email(self.username.data)
        if (not self.user) or self.user.is_deleted or not self.user.is_active:
            # Do a bcrypt comparison so that this path "costs" the same as the one for
            # valid users, because skipping the hash check would be a timing oracle.
            bcrypt.check_password_hash(_TIMING_EQUALIZER_HASH, self.password.data)
            self.form_errors.append(generic_error)
            self.user = None
            return False

        if not self.user.check_password(self.password.data):
            self.form_errors.append(generic_error)
            return False

        return True


class ForgotPasswordForm(FlaskForm):
    """Reset password form."""

    username = StringField(_('Email'), validators=[DataRequired()])

    # To prevent user enumeration we *don't* check for account existence or
    # reset limit here.

class ResetPasswordForm(FlaskForm):
    """Reset password form."""

    code = HiddenField(validators=[DataRequired()])
    username = StringField(_('Email'), validators=[DataRequired()])
    password = PasswordField(_('Password'), validators=[DataRequired(), Length(min=6, max=64)])
    confirm = PasswordField(_('Verify password'),
                            validators=[DataRequired(),
                                        EqualTo('password', message=_('Passwords must match'))])

    def validate(self, extra_validators=None):
        """Validate the form."""
        initial_validation = super(ResetPasswordForm, self).validate(extra_validators)

        if not initial_validation:
            return False

        password_reset = PasswordReset.get_by_email_and_code(self.username.data, self.code.data)
        if password_reset:  # Implies there was also a matching user.
            if password_reset.expires_at < datetime.utcnow():
                self.code.errors.append(_('Reset code "%(code)s" expired at %(isoformat)s',
                                          code=self.code.data,
                                          isoformat=password_reset.expires_at.isoformat() + 'Z'))
                return False
            if not password_reset.is_active:
                self.code.errors.append(_('Reset code "%(code)s" already used (%(isoformat)s)',
                                          code=self.code.data,
                                          isoformat=password_reset.modified_at.isoformat() + 'Z'))
                return False
            return True
        else:
            self.code.errors.append(_('Reset code "%(code)s" does not exit', code=self.code.data))
            return False
