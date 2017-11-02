"""Add OAuth2 tokens.

Revision ID: e18d13a9f276
Revises: f3e929832ba3
Create Date: 2017-10-30 13:56:54.456073

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = 'e18d13a9f276'
down_revision = 'f3e929832ba3'
branch_labels = None
depends_on = None


def upgrade():
    """Create OAuth2 token tables."""
    op.create_table('grants',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('client_id', sa.Integer(), nullable=False),
                    sa.Column('code', sa.String(length=256), nullable=False),
                    sa.Column('redirect_uri', sa.String(length=256), nullable=False),
                    sa.Column('expires_at', sa.DateTime(), nullable=False),
                    sa.Column('scopes', sa.Text(), nullable=False),
                    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'))
    op.create_table('tokens',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('client_id', sa.Integer(), nullable=False),
                    sa.Column('token_type', sa.String(length=40), nullable=False),
                    sa.Column('access_token', sa.String(length=256), nullable=False),
                    sa.Column('refresh_token', sa.String(length=256), nullable=False),
                    sa.Column('expires_at', sa.DateTime(), nullable=False),
                    sa.Column('scopes', sa.Text(), nullable=False),
                    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('access_token'),
                    sa.UniqueConstraint('refresh_token'))


def downgrade():
    """Drop OAuth2 token tables."""
    op.drop_table('tokens')
    op.drop_table('grants')
