"""add visual fields

Revision ID: 0002_add_visual_fields
Revises: 0001_initial_schema
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_add_visual_fields"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("drivers", sa.Column("image_url", sa.String(length=800), nullable=True))
    op.add_column("races", sa.Column("thumbnail_url", sa.String(length=800), nullable=True))


def downgrade():
    op.drop_column("races", "thumbnail_url")
    op.drop_column("drivers", "image_url")
