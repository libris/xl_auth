"""Make user password and friends non-nullable.

Revision ID: c9e1cd58c4a7
Revises: bc2c31758e2a
Create Date: 2017-10-26 16:19:22.453941

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = 'c9e1cd58c4a7'
down_revision = 'bc2c31758e2a'
branch_labels = None
depends_on = None


def upgrade():
    """Make columns 'active', 'is_admin' and 'password' non-nullable."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('active', existing_type=sa.BOOLEAN(), nullable=False)
        batch_op.alter_column('is_admin', existing_type=sa.BOOLEAN(), nullable=False)
        batch_op.alter_column('password', existing_type=sa.BLOB(), nullable=False)


def downgrade():
    """Make things nullable again."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password', existing_type=sa.BLOB(), nullable=True)
        batch_op.alter_column('is_admin', existing_type=sa.BOOLEAN(), nullable=True)
        batch_op.alter_column('active', existing_type=sa.BOOLEAN(), nullable=True)
