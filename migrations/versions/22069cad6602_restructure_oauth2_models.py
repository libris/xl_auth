"""Restructure OAuth2 models.

Revision ID: 22069cad6602
Revises: d7b1b886bf92
Create Date: 2017-11-02 13:41:43.920256

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = '22069cad6602'
down_revision = 'd7b1b886bf92'
branch_labels = None
depends_on = None


def upgrade():
    """Re-create tables 'clients', 'grants' and 'tokens'."""
    op.drop_table('clients')
    op.drop_table('tokens')
    op.drop_table('grants')

    op.create_table(
        'clients',
        sa.Column('client_id', sa.String(length=32), nullable=False),
        sa.Column('client_secret', sa.String(length=256), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('is_confidential', sa.Boolean(), nullable=False),
        sa.Column('_redirect_uris', sa.Text(), nullable=False),
        sa.Column('_default_scopes', sa.Text(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=True),
        sa.Column('description', sa.String(length=400), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('client_id'),
        sa.UniqueConstraint('client_secret')
    )

    op.create_table(
        'grants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.String(length=32), nullable=False),
        sa.Column('code', sa.String(length=256), nullable=False),
        sa.Column('redirect_uri', sa.String(length=256), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('_scopes', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.client_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.String(length=32), nullable=False),
        sa.Column('token_type', sa.String(length=40), nullable=False),
        sa.Column('access_token', sa.String(length=256), nullable=False),
        sa.Column('refresh_token', sa.String(length=256), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('_scopes', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.client_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('access_token'),
        sa.UniqueConstraint('refresh_token')
    )


def downgrade():
    """Revert to old version of tables 'clients', 'grants' and 'tokens'."""
    op.drop_table('tokens')
    op.drop_table('grants')
    op.drop_table('clients')

    op.create_table(
        'grants',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('user_id', sa.INTEGER(), nullable=False),
        sa.Column('client_id', sa.INTEGER(), nullable=False),
        sa.Column('code', sa.VARCHAR(length=256), nullable=False),
        sa.Column('redirect_uri', sa.VARCHAR(length=256), nullable=False),
        sa.Column('expires_at', sa.DATETIME(), nullable=False),
        sa.Column('_scopes', sa.TEXT(), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'tokens',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('user_id', sa.INTEGER(), nullable=False),
        sa.Column('client_id', sa.INTEGER(), nullable=False),
        sa.Column('token_type', sa.VARCHAR(length=40), nullable=False),
        sa.Column('access_token', sa.VARCHAR(length=256), nullable=False),
        sa.Column('refresh_token', sa.VARCHAR(length=256), nullable=False),
        sa.Column('expires_at', sa.DATETIME(), nullable=False),
        sa.Column('_scopes', sa.TEXT(), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('access_token'),
        sa.UniqueConstraint('refresh_token')
    )

    op.create_table(
        'clients',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('client_id', sa.VARCHAR(length=64), nullable=False),
        sa.Column('client_secret', sa.VARCHAR(length=256), nullable=False),
        sa.Column('created_by', sa.INTEGER(), nullable=False),
        sa.Column('is_confidential', sa.BOOLEAN(), nullable=False),
        sa.Column('_redirect_uris', sa.TEXT(), nullable=False),
        sa.Column('_default_scopes', sa.TEXT(), nullable=False),
        sa.Column('name', sa.VARCHAR(length=64), nullable=True),
        sa.Column('description', sa.VARCHAR(length=400), nullable=True),
        sa.CheckConstraint('is_confidential IN (0, 1)'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id'),
        sa.UniqueConstraint('client_secret')
    )
