"""Add modified_by/created_by fields for traceability.

Revision ID: b984311d26d7
Revises: 072487c42d98
Create Date: 2017-11-21 15:50:10.745763

"""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

import sqlalchemy as sa
from alembic import op

from xl_auth.collection.models import Collection
from xl_auth.oauth.client.models import Client
from xl_auth.permission.models import Permission
from xl_auth.user.models import User

# Revision identifiers, used by Alembic.
revision = 'b984311d26d7'
down_revision = '072487c42d98'
branch_labels = None
depends_on = None


def upgrade():
    """Add 'modified_by'/'created_by' cols and backfill clients/collections/users/permissions."""
    # Add columns and constraints.
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

    # Backfill with default admin user, if exists.
    superuser = User.get_by_email('libris@kb.se')
    if superuser:
        for client in Client.query.all():
            client.created_at = datetime.utcnow()
            client.save_as(superuser)

        for collection in Collection.query.all():
            collection.created_by = superuser
            collection.modified_by = superuser
            if not collection.modified_at:
                collection.modified_at = collection.created_at
            if collection.modified_at == collection.created_at:
                if collection.replaced_by:
                    replacement = Collection.query.filter_by(code=collection.replaced_by).first()
                    if replacement.created_at > collection.modified_at:
                        collection.modified_at = replacement.created_at
            collection.save_as(superuser, preserve_modified=True)

        for permission in Permission.query.all():
            permission.created_by = superuser
            permission.modified_by = superuser
            permission.save_as(superuser, preserve_modified=True)

        for user in User.query.all():
            user.created_by_id = superuser.id
            user.modified_by_id = superuser.id
            if not user.modified_at:
                user.modified_at = user.created_at
            user.save_as(superuser, preserve_modified=True)

    # Strictify NOT NULL constraints.
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('created_at', existing_type=sa.DateTime(), nullable=False)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=False)

        batch_op.alter_column('name', existing_type=sa.String(length=64), nullable=False)
        batch_op.alter_column('description', existing_type=sa.String(length=400), nullable=False)

    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=False)

    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=False)


def downgrade():
    """Drop 'modified_by'/'created_by' cols and constraints."""
    # Drop columns and constraints, 'laxify NOT NULL constraints.
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.drop_constraint('users_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.drop_constraint('users_created_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.drop_constraint('permissions_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.drop_constraint('permissions_created_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.drop_constraint('collections_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.drop_constraint('collections_created_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('created_by_id')

    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.alter_column('name', existing_type=sa.String(length=64), nullable=True)
        batch_op.alter_column('description', existing_type=sa.String(length=400), nullable=True)
        batch_op.drop_column('modified_at')
        batch_op.drop_column('created_at')
        batch_op.drop_constraint('clients_modified_by_id_fkey', type_='foreignkey')
        batch_op.drop_column('modified_by_id')
        batch_op.alter_column('created_by_id', new_column_name='created_by')
