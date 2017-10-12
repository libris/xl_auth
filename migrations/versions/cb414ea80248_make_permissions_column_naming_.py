"""Make permissions column naming consistent.

Revision ID: cb414ea80248
Revises: c336664ee988
Create Date: 2017-10-12 11:16:13.605044

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'cb414ea80248'
down_revision = 'c336664ee988'
branch_labels = None
depends_on = None


def upgrade():
    """Rename 'catalogue' and 'register' columns."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.alter_column('catalogue', new_column_name='cataloger')
        batch_op.alter_column('register', new_column_name='registrant')


def downgrade():
    """Undo rename of 'catalogue' and 'register' columns."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.alter_column('cataloger', new_column_name='register')
        batch_op.alter_column('registrant', new_column_name='catalogue')
