"""Stricter constraints.

Revision ID: 0af04e897716
Revises: b984311d26d7
Create Date: 2017-11-22 19:53:33.943793

"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sqlalchemy as sa
from alembic import op

# Revision identifiers, used by Alembic.
revision = '0af04e897716'
down_revision = 'b984311d26d7'
branch_labels = None
depends_on = None


def upgrade():
    """Strictify NOT NULL constraints."""
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
    """Relaxify NOT NULL constraints."""
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=True)

    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=True)

    with op.batch_alter_table('collections', schema=None) as batch_op:
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=True)

    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.alter_column('description', existing_type=sa.String(length=400), nullable=True)
        batch_op.alter_column('name', existing_type=sa.String(length=64), nullable=True)
        batch_op.alter_column('modified_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.alter_column('created_at', existing_type=sa.DateTime(), nullable=True)
        batch_op.alter_column('modified_by_id', existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column('created_by_id', existing_type=sa.Integer(), nullable=True)
