"""Rename catalogue_admin column to cataloging_admin in permissions table.

Revision ID: c336664ee988
Revises: 564f2b578774
Create Date: 2017-10-12 10:27:15.211065

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'c336664ee988'
down_revision = '564f2b578774'
branch_labels = None
depends_on = None


def upgrade():
    """Rename 'catalogue_admin' column to 'cataloging_admin' in permissions table."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.alter_column('catalogue_admin', new_column_name='cataloging_admin')


def downgrade():
    """Rename 'cataloging_admin' column to 'catalogue_admin' in permissions table."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.alter_column('cataloging_admin', new_column_name='catalogue_admin')
