"""Add cataloguing_admin to permissions table.

Revision ID: 564f2b578774
Revises: 1ef27f7e11c8
Create Date: 2017-10-10 16:06:45.827883

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '564f2b578774'
down_revision = '1ef27f7e11c8'
branch_labels = None
depends_on = None


def upgrade():
    """Add column 'catalogue_admin' to permissions table."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('catalogue_admin', sa.Boolean(),
                                      server_default='0', nullable=False))
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.alter_column('catalogue_admin', server_default=None)


def downgrade():
    """Remove column 'catalogue_admin' from permissions table."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.drop_column('catalogue_admin')
