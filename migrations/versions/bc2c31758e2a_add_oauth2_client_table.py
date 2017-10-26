"""Add OAuth2 Client table.

Revision ID: bc2c31758e2a
Revises: b09534921ab0
Create Date: 2017-10-26 14:57:37.549116

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'bc2c31758e2a'
down_revision = 'b09534921ab0'
branch_labels = None
depends_on = None


def upgrade():
    """Add OAuth2 Client table."""
    op.create_table('clients',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('client_id', sa.String(length=64), nullable=False),
                    sa.Column('client_secret', sa.String(length=256), nullable=False),
                    sa.Column('created_by', sa.Integer(), nullable=False),
                    sa.Column('is_confidential', sa.Boolean(), nullable=False),
                    sa.Column('redirect_uris', sa.Text(), nullable=False),
                    sa.Column('default_scopes', sa.Text(), nullable=False),
                    sa.Column('name', sa.String(length=64), nullable=True),
                    sa.Column('description', sa.String(length=400), nullable=True),
                    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('client_id'),
                    sa.UniqueConstraint('client_secret'))


def downgrade():
    """Drop OAuth2 Client table."""
    op.drop_table('clients')
