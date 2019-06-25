
"""add is_super column to collections.

Revision ID: 0bd56c203d39
Revises: ba020591fae8
Create Date: 2019-06-24 16:09:54.619016

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = '0bd56c203d39'
down_revision = 'ba020591fae8'
branch_labels = None
depends_on = None


def upgrade():
    """Add column 'is_super' to collections table."""
    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_super', sa.Boolean(), nullable=True))


def downgrade():
    """Remove column 'is_super' from collections table."""
    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.drop_column('is_super')
