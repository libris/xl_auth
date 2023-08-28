"""Add 'tos_approved_at' to User.

Revision ID: 7f3f1a931278
Revises: b984311d26d7
Create Date: 2017-11-29 14:42:23.349903

"""


import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = '7f3f1a931278'
down_revision = 'b984311d26d7'
branch_labels = None
depends_on = None


def upgrade():
    """Add 'users.tos_approved_at' column."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tos_approved_at', sa.DateTime(), nullable=True))


def downgrade():
    """Drop 'users.tos_approved_at' column."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('tos_approved_at')
