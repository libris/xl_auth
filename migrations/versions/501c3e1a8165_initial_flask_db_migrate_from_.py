"""Initial `flask db migrate`, from cookiecutter-flask app.

Revision ID: 501c3e1a8165
Revises:
Create Date: 2017-09-11 13:38:12.860511

"""

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = '501c3e1a8165'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Setup database to initial cookiecutter-flask model."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=80), nullable=False),
        sa.Column('password', sa.Binary(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('first_name', sa.String(length=30), nullable=True),
        sa.Column('last_name', sa.String(length=30), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )


def downgrade():
    """Database downgrade to initial state (empty)."""
    op.drop_table('roles')
    op.drop_table('users')
