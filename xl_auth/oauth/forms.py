"""OAuth forms."""


from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import HiddenField


class AuthorizeForm(FlaskForm):
    """OAuth2'orize form."""

    confirm = HiddenField(_('Confirm'), default='y')

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(AuthorizeForm, self).__init__(*args, **kwargs)
        self.process()
