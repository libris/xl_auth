"""User models."""

from __future__ import absolute_import, division, print_function, unicode_literals

import hashlib
from binascii import hexlify
from datetime import datetime, timedelta
from os import urandom
import uuid

from flask import current_app, url_for
from flask_babel import lazy_gettext as _
from flask_emails import Message
from flask_login import UserMixin
from sqlalchemy import desc
from sqlalchemy.ext.hybrid import hybrid_property

from ..database import Column, Model, SurrogatePK, db, or_, reference_col, relationship
from ..extensions import bcrypt
from ..utils import get_remote_addr


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col('users', nullable=True)
    user = relationship('User', back_populates='roles')

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)


class PasswordReset(SurrogatePK, Model):
    """Password reset token for a user."""

    __tablename__ = 'password_resets'
    user_id = reference_col('users', nullable=True)
    user = relationship('User', back_populates='password_resets')
    code = Column(db.String(32), unique=True, nullable=False)
    is_active = Column(db.Boolean(), default=True, nullable=False)
    expires_at = Column(db.DateTime, nullable=False,
                        default=lambda: datetime.utcnow() + timedelta(hours=7 * 24))

    modified_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user, **kwargs):
        """Create instance."""
        db.Model.__init__(self, user=user, code=self._get_rand_hex_str(32), **kwargs)

    @staticmethod
    def get_by_email_and_code(email, code):
        """Get by `(email, code)` pair."""
        user = User.get_by_email(email)
        if user:
            return PasswordReset.query.filter_by(code=code, user=user).first()

    @staticmethod
    def delete_all_by_user(user):
        """Delete all password resets for specified user."""
        PasswordReset.query.filter_by(user=user).delete()

    @hybrid_property
    def is_recent(self):
        """Check if reset was created recently."""
        return self.created_at > (datetime.utcnow() - timedelta(hours=2))

    def send_email(self, account_registration_from_user=None):
        """Email password reset link to the user, possibly in wording of initial registration."""
        password_reset_url = url_for('public.reset_password', email=self.user.email,
                                     code=self.code, _external=True)
        service_name = current_app.config['SERVER_NAME'] or current_app.config['APP_NAME']
        if account_registration_from_user:
            subject = _('Account activation and password reset for %(username)s '
                        'at %(server_name)s', username=self.user.email, server_name=service_name)
            body_text = _(
                'Hello %(full_name)s,'
                '\n\n'
                'You have been granted a user account at %(server_name)s by %(current_user)s. '
                'Use the secret link below to set a personal account password, and \
thereby activating your account:'
                '\n\n'
                '%(password_reset_url)s'
                '\n\n\n\n'
                'P.S. If you received this mail for no obvious reason, please inform us about it \
at libris@kb.se!'
                '\n\n',
                full_name=self.user.full_name, server_name=service_name,
                current_user=account_registration_from_user.email,
                password_reset_url=password_reset_url
            )
            body_html = _(
                '<p>'
                'Hello %(full_name)s,'
                '<br/><br/>'
                'You have been granted a user account at %(server_name)s by %(current_user)s. '
                'Use the secret link below to set a personal password, and \
thereby activating your account:'
                '<br/><br/>'
                '<a href="%(password_reset_url)s">%(password_reset_url)s</a>'
                '<br/><br/>'
                '</p>'
                '<p><small>'
                'P.S. If you received this mail for no obvious reason, please inform us about it '
                'at <a href="mailto:libris@kb.se">libris@kb.se</a>!'
                '</small></p>',
                full_name=self.user.full_name, server_name=service_name,
                current_user='<a href="mailto:{0}">{0}</a>'.format(
                    account_registration_from_user.email),
                password_reset_url=password_reset_url
            )

        else:
            subject = _('Password reset for %(username)s at %(server_name)s',
                        username=self.user.email, server_name=service_name)
            body_text = _(
                'Hello %(full_name)s,'
                '\n\n'
                'Here is the secret link for resetting your personal account password:'
                '\n\n'
                '%(password_reset_url)s'
                '\n\n\n\n'
                'P.S. If you received this mail for no obvious reason, please inform us about it \
at libris@kb.se!'
                '\n\n',
                full_name=self.user.full_name, password_reset_url=password_reset_url
            )
            body_html = _(
                '<p>'
                'Hello %(full_name)s,'
                '<br/><br/>'
                'Here is the secret link for resetting your personal account password:'
                '<br/><br/>'
                '<a href="%(password_reset_url)s">%(password_reset_url)s</a>'
                '<br/><br/>'
                '</p>'
                '<p><small>'
                'P.S. If you received this mail for no obvious reason, please inform us about it '
                'at <a href="mailto:libris@kb.se">libris@kb.se</a>!'
                '</small></p>',
                full_name=self.user.full_name, password_reset_url=password_reset_url
            )

        result = Message(
            subject=subject,
            mail_to=(self.user.full_name, self.user.email),
            text=body_text,
            html=body_html
        ).send()

        if not hasattr(result, 'status_code'):
            result = result[0]

        assert result.status_code == 250

    @property
    def display_value(self):
        return f"{self.user.email}: {self.created_at}"

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<PasswordReset({email!r})>'.format(email=self.user.email)


class FailedLoginAttempt(SurrogatePK, Model):
    """A failed login attempt."""

    __tablename__ = 'failed_login_attempts'
    username = Column(db.String(255), unique=False, nullable=False)
    remote_addr = Column(db.String(255), unique=False, nullable=False)

    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, username, remote_addr):
        """Create instance."""
        db.Model.__init__(self, username=username, remote_addr=remote_addr)

    @staticmethod
    def too_many_recent_failures_for(username):
        """Determine if a login attempt is allowed or not."""
        timeframe = current_app.config['XL_AUTH_FAILED_LOGIN_TIMEFRAME']
        from_timestamp = datetime.utcnow() - timedelta(seconds=timeframe)
        attempts = FailedLoginAttempt.query.filter(
            FailedLoginAttempt.username.ilike(username),
            FailedLoginAttempt.created_at >= from_timestamp).all()
        if len(attempts) >= current_app.config['XL_AUTH_FAILED_LOGIN_MAX_ATTEMPTS']:
            return True
        else:
            return False

    @staticmethod
    def get_all_by_user(user):
        """Get all failed login attempts for specified user."""
        return FailedLoginAttempt.query.filter_by(username=user.email).order_by(desc('created_at')).all()

    @staticmethod
    def delete_all_by_user(user):
        """Delete all failed login attempts for specified user."""
        FailedLoginAttempt.query.filter_by(username=user.email).delete()

    @property
    def display_value(self):
        return f"{self.username}: {self.created_at}, {self.remote_addr}"

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<FailedLoginAttempt({id}:{username!r})>'.format(id=self.id, username=self.username)


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = Column(db.String(255), unique=True, nullable=False)
    full_name = Column(db.String(255), unique=False, nullable=False)
    password = Column(db.LargeBinary(128), nullable=False)
    last_login_at = Column(db.DateTime, default=None)
    tos_approved_at = Column(db.DateTime, default=None)
    is_active = Column(db.Boolean(), default=False, nullable=False)
    is_deleted = Column(db.Boolean(), default=False, nullable=False)
    is_admin = Column(db.Boolean(), default=False, nullable=False)
    permissions = relationship('Permission', back_populates='user',
                               foreign_keys='Permission.user_id', lazy='joined')
    roles = relationship('Role', back_populates='user')
    password_resets = relationship('PasswordReset', back_populates='user')

    modified_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                         nullable=False)
    modified_by_id = reference_col('users', nullable=False)
    modified_by = relationship('User', remote_side=id, foreign_keys=modified_by_id)

    created_at = Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = reference_col('users', nullable=False)
    created_by = relationship('User', remote_side=id, foreign_keys=created_by_id)

    def __init__(self, email, full_name, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, email=email, full_name=full_name, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.set_password(hexlify(urandom(16)))

    @staticmethod
    def get_by_email(email):
        """Get by email."""
        return User.query.filter(User.email.ilike(email)).first()

    @staticmethod
    def get_modified_and_created_by_user(user):
        """Get all users (except itself) created or modified by specified user."""
        return (User.query
                .filter(or_(User.created_by == user, User.modified_by == user))
                .filter(User.id != user.id)
                .all())

    @hybrid_property
    def is_cataloging_admin(self):
        """Return 'cataloging_admin' status."""
        for permission in self.permissions:
            if permission.cataloging_admin:
                return True
        return False

    @hybrid_property
    def is_global_registrant(self):
        """Return 'global_registrant' status."""
        return any(
            permission.global_registrant and
            permission.collection.is_active
            for permission in self.permissions
        )

    @hybrid_property
    def can_see_global_registrant(self):
        """Check if the user is allowed to see 'global_registrant' status."""
        return self.is_admin or self.is_global_registrant

    def is_cataloging_admin_for(self, *collections):
        """Check if user has 'cataloging_admin' permissions for all 'collections'."""
        collections = set(collections)
        if not collections:
            return False  # Can't be cataloging admin for nothing
        admin_permission_collections = set(_.collection for _ in self.permissions
                                           if _.cataloging_admin)
        return collections.issubset(admin_permission_collections)

    def has_any_permission_for(self, collection):
        """Check for any permission on a specific collection."""
        return any([permission for permission in self.permissions
                    if permission.collection == collection])

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def set_email(self, email):
        """Set email."""
        self.email = email

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    def update_last_login(self):
        self.update_last_login_internal(remote_address=get_remote_addr())

    def update_last_login_internal(self, remote_address, commit=True):
        """Remove failed login attempts for username/IP."""
        (FailedLoginAttempt.query.filter(FailedLoginAttempt.username.ilike(self.email),
                                         FailedLoginAttempt.remote_addr == remote_address)
                                 .delete(synchronize_session=False))

        """Set 'last_login_at' to current datetime."""
        self.last_login_at = datetime.utcnow()
        if commit:
            self.save(commit=True, preserve_modified=True)

    def set_tos_approved(self, commit=True):
        """Set 'tos_approved_at' to current datetime."""
        self.tos_approved_at = datetime.utcnow()
        if commit:
            self.save(commit=True, preserve_modified=True)

    def get_gravatar_url(self, size=32):
        """Get Gravatar URL."""
        hashed_email = hashlib.md5(str(self.email).lower().encode()).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=mm&s={}'.format(hashed_email, size)

    def get_permissions_label_help_text_as_seen_by(self, current_user):
        """Return help text for permissions label."""
        if current_user == self or current_user.is_admin:
            return ''
        elif current_user.is_cataloging_admin:
            return _('You will only see permissions for those collections that you are '
                     'cataloging admin for.')
        else:
            # This text is never shown to regular users viewing another user
            return ''

    def get_permissions_as_seen_by(self, current_user):
        """Return subset of permissions viewable by 'current_user'."""
        if current_user == self or current_user.is_admin:
            return self.permissions
        else:
            def current_user_is_cataloging_admin_for(collection):
                for permission in current_user.permissions:
                    if permission.collection == collection and permission.cataloging_admin:
                        return True
                return False

            return [perm for perm in self.permissions
                    if current_user_is_cataloging_admin_for(perm.collection)]

    def get_cataloging_admin_permissions(self):
        """Return all cataloging admin permissions for this user."""
        return [perm for perm in self.permissions if perm.cataloging_admin]

    def get_active_and_recent_password_resets(self):
        """Return a list of active and recent password resets for this user."""
        return [reset for reset in self.password_resets if reset.is_active and reset.is_recent]

    @property
    def display_name(self):
        if self.is_deleted:
            return _('Deleted user')
        return self.full_name

    def save_as(self, current_user, commit=True, preserve_modified=False):
        """Save instance as 'current_user'."""
        if current_user and not self.created_at:
            self.created_by = current_user
        if current_user and not preserve_modified:
            self.modified_by_id = current_user.id
            # Using ``self.modified_by = current_user`` yields an error when user modifies itself:
            # "sqlalchemy.exc.CircularDependencyError: Circular dependency detected."
        return self.save(commit=commit, preserve_modified=preserve_modified)

    def soft_delete(self):
        """Soft delete instance."""
        for permission in self.permissions:
            permission.delete()
        for password_reset in self.password_resets:
            password_reset.delete()
        self.email = f"DELETED-{str(uuid.uuid4())}"
        self.is_active = False
        self.is_deleted = True
        self.full_name = "DELETED"
        return self.save(commit=True)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({email!r})>'.format(email=self.email)
