"""Add modified_by/created_by fields for traceability.

Revision ID: b984311d26d7
Revises: 072487c42d98
Create Date: 2017-11-21 15:50:10.745763

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = 'b984311d26d7'
down_revision = '072487c42d98'
branch_labels = None
depends_on = None


def upgrade():
    """Add 'modified_by'/'created_by' cols and backfill clients/collections/users/permissions."""
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.alter_column('created_by', new_column_name='created_by_id')
        batch_op.add_column(sa.Column('modified_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('clients_modified_by_id_fkey', 'users',
                                    ['modified_by_id'], ['id'])
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('modified_at', sa.DateTime(), nullable=True))

    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('collections_created_by_id_fkey', 'users',
                                    ['created_by_id'], ['id'])
        batch_op.add_column(sa.Column('modified_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('collections_modified_by_id_fkey', 'users',
                                    ['modified_by_id'], ['id'])

    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('permissions_created_by_id_fkey', 'users',
                                    ['created_by_id'], ['id'])
        batch_op.add_column(sa.Column('modified_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('permissions_modified_by_id_fkey', 'users',
                                    ['modified_by_id'], ['id'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('users_created_by_id_fkey', 'users',
                                    ['created_by_id'], ['id'])
        batch_op.add_column(sa.Column('modified_by_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('users_modified_by_id_fkey', 'users',
                                    ['modified_by_id'], ['id'])


def downgrade():
    """Drop 'modified_by'/'created_by' cols and constraints."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('users_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.drop_constraint('users_created_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.drop_constraint('permissions_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.drop_constraint('permissions_created_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.drop_constraint('collections_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.drop_constraint('collections_created_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.drop_column('modified_at')
        batch_op.drop_column('created_at')
        batch_op.drop_constraint('clients_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.alter_column('created_by_id', new_column_name='created_by')
