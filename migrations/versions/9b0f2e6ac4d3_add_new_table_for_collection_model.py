"""Add new table for Collection model.

Revision ID: 9b0f2e6ac4d3
Revises: bbfcebd395a0
Create Date: 2017-09-14 17:11:25.710882

"""

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = '9b0f2e6ac4d3'
down_revision = 'bbfcebd395a0'
branch_labels = None
depends_on = None


def upgrade():
    """Create 'collections' table."""
    op.create_table(
        'collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=255), nullable=False),
        sa.Column('friendly_name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=255), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )


def downgrade():
    """Drop 'collections' table."""
    op.drop_table('collections')
