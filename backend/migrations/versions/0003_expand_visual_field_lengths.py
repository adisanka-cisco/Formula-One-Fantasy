"""expand visual field lengths

Revision ID: 0003_expand_visual_field_lengths
Revises: 0002_add_visual_fields
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_expand_visual_field_lengths"
down_revision = "0002_add_visual_fields"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("drivers") as batch_op:
        batch_op.alter_column("image_url", existing_type=sa.String(length=800), type_=sa.String(length=4000), existing_nullable=True)
    with op.batch_alter_table("races") as batch_op:
        batch_op.alter_column("thumbnail_url", existing_type=sa.String(length=800), type_=sa.String(length=4000), existing_nullable=True)


def downgrade():
    with op.batch_alter_table("drivers") as batch_op:
        batch_op.alter_column("image_url", existing_type=sa.String(length=4000), type_=sa.String(length=800), existing_nullable=True)
    with op.batch_alter_table("races") as batch_op:
        batch_op.alter_column("thumbnail_url", existing_type=sa.String(length=4000), type_=sa.String(length=800), existing_nullable=True)
