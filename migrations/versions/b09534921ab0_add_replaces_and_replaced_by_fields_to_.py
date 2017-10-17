"""Add 'replaces' and 'replaced_by' fields to collections table.

Revision ID: b09534921ab0
Revises: cb414ea80248
Create Date: 2017-10-12 17:40:50.991129

"""
import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = 'b09534921ab0'
down_revision = 'cb414ea80248'
branch_labels = None
depends_on = None


def upgrade():
    """Add columns 'replaces' and 'replaced_by' to collections table."""
    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('replaced_by', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('replaces', sa.String(length=255), nullable=True))


def downgrade():
    """Drop columns 'replaces' and 'replaced_by' in collections table."""
    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.drop_column('replaces')
        batch_op.drop_column('replaced_by')
