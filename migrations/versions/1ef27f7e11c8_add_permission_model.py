"""Add new table for Permission model.

Revision ID: 1ef27f7e11c8
Revises: 9b0f2e6ac4d3
Create Date: 2017-09-28 21:08:25.130167

"""

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = '1ef27f7e11c8'
down_revision = '9b0f2e6ac4d3'
branch_labels = None
depends_on = None


def upgrade():
    """Create 'permissions' table."""
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('collection_id', sa.Integer(), nullable=False),
        sa.Column('register', sa.Boolean(), nullable=False),
        sa.Column('catalogue', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'collection_id')
    )


def downgrade():
    """Drop 'permissions' table."""
    op.drop_table('permissions')
