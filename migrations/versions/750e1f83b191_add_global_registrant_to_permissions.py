"""Add global_registrant to permissions.

Revision ID: 750e1f83b191
Revises: ba020591fae8
Create Date: 2019-06-27 07:38:22.728758

"""


import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = '750e1f83b191'
down_revision = u'ba020591fae8'
branch_labels = None
depends_on = None


def upgrade():
    """Add column 'global_registrant' to permissions table."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('global_registrant', sa.Boolean(),
                                      server_default='0', nullable=False))
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.alter_column('global_registrant', server_default=None)


def downgrade():
    """Remove column 'global_registrant' from permissions table."""
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.drop_column('global_registrant')
