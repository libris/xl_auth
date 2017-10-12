"""Make permissions column naming consistent.

Revision ID: cb414ea80248
Revises: c336664ee988
Create Date: 2017-10-12 11:16:13.605044

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'cb414ea80248'
down_revision = 'c336664ee988'
branch_labels = None
depends_on = None


def upgrade():
    """Rename 'catalogue' and 'register' columns."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cataloger', sa.Boolean(), nullable=False))
        batch_op.add_column(sa.Column('registrant', sa.Boolean(), nullable=False))
        batch_op.drop_column('catalogue')
        batch_op.drop_column('register')


def downgrade():
    """Undo rename of 'catalogue' and 'register' columns."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('register', sa.BOOLEAN(), nullable=False))
        batch_op.add_column(sa.Column('catalogue', sa.BOOLEAN(), nullable=False))
        batch_op.drop_column('registrant')
        batch_op.drop_column('cataloger')
