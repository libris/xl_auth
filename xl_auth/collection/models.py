"""Collection model."""


from datetime import datetime

from flask_babel import lazy_gettext as _

from ..database import Column, Model, SurrogatePK, db, or_, reference_col, relationship


class Collection(SurrogatePK, Model):
    """A collection of library stuff, a.k.a. 'a sigel'."""

    __tablename__ = 'collections'
    code = Column(db.String(255), unique=True, nullable=False)
    friendly_name = Column(db.String(255), unique=False, nullable=False)
    category = Column(db.String(255), nullable=False)
    is_active = Column(db.Boolean(), default=True)
    permissions = relationship('Permission', back_populates='collection', lazy='joined')
    replaces = Column(db.String(255))
    replaced_by = Column(db.String(255))

    modified_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                         nullable=False)
    modified_by_id = reference_col('users', nullable=False)
    modified_by = relationship('User', foreign_keys=modified_by_id)

    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = reference_col('users', nullable=False)
    created_by = relationship('User', foreign_keys=created_by_id)

    def __init__(self, code, friendly_name, category, **kwargs):
        """Create instance."""
        db.Model.__init__(self, code=code, friendly_name=friendly_name, category=category,
                          **kwargs)

    @staticmethod
    def get_by_code(code):
        """Get by collection code."""
        return Collection.query.filter_by(code=code).first()

    def get_permissions_label_help_text_as_seen_by(self, current_user):
        """Return help text for permissions label."""
        if not (current_user.is_cataloging_admin_for(self) or current_user.is_admin):
            return _('You will only see all permissions for those collections that you are '
                     'cataloging admin for.')
        else:
            return ''

    @staticmethod
    def get_modified_and_created_by_user(user):
        """Get all collections created or modified by specified user."""
        return Collection.query.filter(or_(Collection.created_by == user,
                                           Collection.modified_by == user)).all()

    def get_permissions_as_seen_by(self, current_user):
        """Return subset of permissions viewable by 'current_user'."""
        if current_user.is_cataloging_admin_for(self) or current_user.is_admin:
            return self.permissions
        else:
            def is_cataloging_admin_or_own_permissions(test_permission):
                return test_permission.user == current_user or test_permission.cataloging_admin
            return list(filter(is_cataloging_admin_or_own_permissions, self.permissions))

    def get_replaces_and_replaced_by_str(self):
        """Build string with replaces/replaced-by info."""
        if self.replaced_by and self.replaces:
            return _('Replaces %(replaces_code)s, then replaced by %(replaced_by_code)s',
                     replaces_code=self.replaces, replaced_by_code=self.replaced_by)
        elif self.replaces:
            return _('Replaces %(replaces_code)s', replaces_code=self.replaces)
        elif self.replaced_by:
            return _('Replaced by %(replaced_by_code)s', replaced_by_code=self.replaced_by)
        else:
            return ''

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Collection({code!r})>'.format(code=self.code)
