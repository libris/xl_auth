"""Add PKCE columns to grants.

Revision ID: c8d4a1f0b2e6
Revises: 14302cf25610
Create Date: 2026-11-06 15:20:00.000000

"""


import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = 'c8d4a1f0b2e6'
down_revision = '14302cf25610'
branch_labels = None
depends_on = None


def upgrade():
    """Add PKCE 'code_challenge' and 'code_challenge_method' columns to grants."""
    with op.batch_alter_table('grants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('code_challenge', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('code_challenge_method', sa.String(length=10),
                                      nullable=True))


def downgrade():
    """Remove PKCE columns from grants."""
    with op.batch_alter_table('grants', schema=None) as batch_op:
        batch_op.drop_column('code_challenge_method')
        batch_op.drop_column('code_challenge')
