"""Rename "active" columns to "is_active".

Revision ID: 072487c42d98
Revises: 32839e658194
Create Date: 2017-11-14 15:46:33.118004

"""


from alembic import op

# Revision identifiers, used by Alembic.
revision = '072487c42d98'
down_revision = '32839e658194'
branch_labels = None
depends_on = None


def upgrade():
    """Rename 'active' column to 'is_active' in users and collections tables."""
    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.alter_column('active', new_column_name='is_active')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('active', new_column_name='is_active')


def downgrade():
    """Rename 'is_active' column to 'active' in users and collections tables."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('is_active', new_column_name='active')

    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.alter_column('is_active', new_column_name='active')
