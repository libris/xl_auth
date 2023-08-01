"""Make scope and friends into lists instead of strings.

Revision ID: d7b1b886bf92
Revises: e18d13a9f276
Create Date: 2017-11-01 12:54:40.739492

"""


from alembic import op

# Revision identifiers, used by Alembic.
revision = 'd7b1b886bf92'
down_revision = 'e18d13a9f276'
branch_labels = None
depends_on = None


def upgrade():
    """Rename columns with list data into _columns (with hybrid-properties)."""
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.alter_column('default_scopes', new_column_name='_default_scopes')
        batch_op.alter_column('redirect_uris', new_column_name='_redirect_uris')

    with op.batch_alter_table('grants', schema=None) as batch_op:
        batch_op.alter_column('scopes', new_column_name='_scopes')

    with op.batch_alter_table('tokens', schema=None) as batch_op:
        batch_op.alter_column('scopes', new_column_name='_scopes')


def downgrade():
    """Revert renaming of list data columns."""
    with op.batch_alter_table('tokens', schema=None) as batch_op:
        batch_op.alter_column('_scopes', new_column_name='scopes')

    with op.batch_alter_table('grants', schema=None) as batch_op:
        batch_op.alter_column('_scopes', new_column_name='scopes')

    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.alter_column('_redirect_uris', new_column_name='redirect_uris')
        batch_op.alter_column('_default_scopes', new_column_name='default_scopes')
