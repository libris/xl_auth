"""Add failed login attempt table.

Revision ID: 55513723546e
Revises: 7f3f1a931278
Create Date: 2018-01-04 13:01:52.499521

"""


import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = '55513723546e'
down_revision = '7f3f1a931278'
branch_labels = None
depends_on = None


def upgrade():
    """Create 'failed_login_attempts' table."""
    op.create_table('failed_login_attempts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username', sa.String(length=255), nullable=False),
                    sa.Column('remote_addr', sa.String(length=255), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint('id'))


def downgrade():
    """Drop 'failed_login_attempts' table."""
    op.drop_table('failed_login_attempts')
