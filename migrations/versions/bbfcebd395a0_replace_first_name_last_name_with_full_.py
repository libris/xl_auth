"""Replace username with email as the unique identifier.

Revision ID: bbfcebd395a0
Revises: 501c3e1a8165
Create Date: 2017-09-13 16:18:32.473558

"""

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = 'bbfcebd395a0'
down_revision = '501c3e1a8165'
branch_labels = None
depends_on = None


def upgrade():
    """Drop 'username', replace first/last name with 'full_name' and set email to String(255)."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('full_name', sa.String(length=255), nullable=False))
        batch_op.alter_column('email', existing_type=sa.VARCHAR(length=80),
                              type_=sa.String(length=255), existing_nullable=False)
        batch_op.drop_column('first_name')
        batch_op.drop_column('last_name')
        batch_op.drop_column('username')


def downgrade():
    """Drop 'full_name', add 'username', 'first_name', 'last_name', set email to VARCHAR(80)."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.VARCHAR(length=80), nullable=False))
        batch_op.add_column(sa.Column('last_name', sa.VARCHAR(length=30), nullable=True))
        batch_op.add_column(sa.Column('first_name', sa.VARCHAR(length=30), nullable=True))
        batch_op.alter_column('email', existing_type=sa.String(length=255),
                              type_=sa.VARCHAR(length=80), existing_nullable=False)
        batch_op.drop_column('full_name')
