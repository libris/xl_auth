"""Add optional user to OAuth2 client.

Revision ID: ba020591fae8
Revises: a6c5437cfd80
Create Date: 2018-08-21 12:58:24.101819

"""


import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = 'ba020591fae8'
down_revision = 'a6c5437cfd80'
branch_labels = None
depends_on = None


def upgrade():
    """Add user column to client table."""
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_client_user_id', 'users', ['user_id'], ['id'])


def downgrade():
    """Remove user column from client table."""
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.drop_constraint('fk_client_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')
