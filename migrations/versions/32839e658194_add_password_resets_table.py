"""Add new table for PasswordReset model.

Revision ID: 32839e658194
Revises: 22069cad6602
Create Date: 2017-11-13 08:12:28.990037

"""


import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = '32839e658194'
down_revision = '22069cad6602'
branch_labels = None
depends_on = None


def upgrade():
    """Create 'password_resets' table."""
    op.create_table(
        'password_resets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('code', sa.String(length=32), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('modified_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )


def downgrade():
    """Drop 'password_resets' table."""
    op.drop_table('password_resets')
