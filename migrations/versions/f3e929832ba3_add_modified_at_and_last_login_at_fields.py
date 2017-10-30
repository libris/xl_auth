"""Add 'modified_at' and 'last_login_at' fields.

Revision ID: f3e929832ba3
Revises: c9e1cd58c4a7
Create Date: 2017-10-30 13:54:26.596122

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = 'f3e929832ba3'
down_revision = 'c9e1cd58c4a7'
branch_labels = None
depends_on = None


def upgrade():
    """Add 'modified_at' column for Collection/Permission/User, and 'last_login_at' for User."""
    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('modified_at', sa.DateTime(), nullable=True))

    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('modified_at', sa.DateTime(), nullable=True))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_login_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('modified_at', sa.DateTime(), nullable=True))


def downgrade():
    """Drop 'modified_at' and 'last_login_at' columns."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('modified_at')
        batch_op.drop_column('last_login_at')

    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.drop_column('modified_at')

    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.drop_column('modified_at')
