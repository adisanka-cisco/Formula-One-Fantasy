"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-22
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nickname", sa.String(length=80), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("subscription_tier", sa.String(length=40), nullable=False),
        sa.Column("credit_balance", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("fantasy_score", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_nickname"), "users", ["nickname"], unique=True)

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("short_name", sa.String(length=40), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("short_name"),
    )

    op.create_table(
        "payment_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("payment_customer_id", sa.String(length=120), nullable=False),
        sa.Column("payment_brand", sa.String(length=40), nullable=False),
        sa.Column("payment_last4", sa.String(length=4), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payment_profiles_user_id"), "payment_profiles", ["user_id"], unique=False)

    op.create_table(
        "drivers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("driver_code", sa.String(length=8), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=False),
        sa.Column("last_name", sa.String(length=120), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_drivers_driver_code"), "drivers", ["driver_code"], unique=True)
    op.create_index(op.f("ix_drivers_team_id"), "drivers", ["team_id"], unique=False)

    op.create_table(
        "races",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.Column("race_name", sa.String(length=160), nullable=False),
        sa.Column("circuit_name", sa.String(length=160), nullable=False),
        sa.Column("country", sa.String(length=120), nullable=False),
        sa.Column("race_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("season", "round", name="uq_races_season_round"),
    )
    op.create_index(op.f("ix_races_season"), "races", ["season"], unique=False)

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("race_id", sa.Integer(), nullable=False),
        sa.Column("stake_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("locked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["race_id"], ["races.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "race_id", name="uq_predictions_user_race"),
    )
    op.create_index(op.f("ix_predictions_race_id"), "predictions", ["race_id"], unique=False)
    op.create_index(op.f("ix_predictions_user_id"), "predictions", ["user_id"], unique=False)

    op.create_table(
        "race_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("race_id", sa.Integer(), nullable=False),
        sa.Column("result_type", sa.String(length=40), nullable=False),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("driver_id", sa.Integer(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"]),
        sa.ForeignKeyConstraint(["race_id"], ["races.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_race_results_race_id"), "race_results", ["race_id"], unique=False)
    op.create_index(op.f("ix_race_results_result_type"), "race_results", ["result_type"], unique=False)

    op.create_table(
        "prediction_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("prediction_id", sa.Integer(), nullable=False),
        sa.Column("prediction_type", sa.String(length=40), nullable=False),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("driver_id", sa.Integer(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("points_awarded", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"]),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_prediction_items_prediction_id"), "prediction_items", ["prediction_id"], unique=False)
    op.create_index(op.f("ix_prediction_items_prediction_type"), "prediction_items", ["prediction_type"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_prediction_items_prediction_type"), table_name="prediction_items")
    op.drop_index(op.f("ix_prediction_items_prediction_id"), table_name="prediction_items")
    op.drop_table("prediction_items")
    op.drop_index(op.f("ix_race_results_result_type"), table_name="race_results")
    op.drop_index(op.f("ix_race_results_race_id"), table_name="race_results")
    op.drop_table("race_results")
    op.drop_index(op.f("ix_predictions_user_id"), table_name="predictions")
    op.drop_index(op.f("ix_predictions_race_id"), table_name="predictions")
    op.drop_table("predictions")
    op.drop_index(op.f("ix_races_season"), table_name="races")
    op.drop_table("races")
    op.drop_index(op.f("ix_drivers_team_id"), table_name="drivers")
    op.drop_index(op.f("ix_drivers_driver_code"), table_name="drivers")
    op.drop_table("drivers")
    op.drop_index(op.f("ix_payment_profiles_user_id"), table_name="payment_profiles")
    op.drop_table("payment_profiles")
    op.drop_table("teams")
    op.drop_index(op.f("ix_users_nickname"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

