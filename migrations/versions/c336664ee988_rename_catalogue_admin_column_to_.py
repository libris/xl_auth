"""Rename catalogue_admin column to cataloging_admin in permissions table.

Revision ID: c336664ee988
Revises: 564f2b578774
Create Date: 2017-10-12 10:27:15.211065

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c336664ee988'
down_revision = '564f2b578774'
branch_labels = None
depends_on = None


def upgrade():
    """Rename 'catalogue_admin' column to 'cataloging_admin' in permissions table."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cataloging_admin', sa.Boolean(), nullable=False))
        batch_op.drop_column('catalogue_admin')


def downgrade():
    """Rename 'cataloging_admin' column to 'catalogue_admin' in permissions table."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('catalogue_admin', sa.BOOLEAN(), nullable=False))
        batch_op.drop_column('cataloging_admin')
