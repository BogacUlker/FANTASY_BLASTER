"""Initial database schema.

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE usertier AS ENUM ('free', 'pro', 'premium')")
    op.execute(
        "CREATE TYPE injurystatus AS ENUM ('healthy', 'questionable', 'doubtful', 'out', 'day_to_day')"
    )

    # Create teams table
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nba_team_id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("abbreviation", sa.String(length=10), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("conference", sa.String(length=20), nullable=True),
        sa.Column("division", sa.String(length=30), nullable=True),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nba_team_id"),
    )
    op.create_index(op.f("ix_teams_abbreviation"), "teams", ["abbreviation"], unique=False)

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=True, default=False),
        sa.Column(
            "tier",
            sa.Enum("free", "pro", "premium", name="usertier"),
            nullable=True,
            server_default="free",
        ),
        sa.Column("yahoo_access_token", sa.Text(), nullable=True),
        sa.Column("yahoo_refresh_token", sa.Text(), nullable=True),
        sa.Column("yahoo_token_expires", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # Create players table
    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nba_player_id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("position", sa.String(length=20), nullable=True),
        sa.Column("height", sa.String(length=10), nullable=True),
        sa.Column("weight", sa.Integer(), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column(
            "injury_status",
            sa.Enum(
                "healthy",
                "questionable",
                "doubtful",
                "out",
                "day_to_day",
                name="injurystatus",
            ),
            nullable=True,
            server_default="healthy",
        ),
        sa.Column("injury_note", sa.Text(), nullable=True),
        sa.Column("headshot_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["teams.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nba_player_id"),
    )
    op.create_index(op.f("ix_players_name"), "players", ["name"], unique=False)
    op.create_index(op.f("ix_players_team_id"), "players", ["team_id"], unique=False)

    # Create player_game_stats table
    op.create_table(
        "player_game_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.String(length=50), nullable=False),
        sa.Column("game_date", sa.Date(), nullable=False),
        sa.Column("opponent_team_id", sa.Integer(), nullable=True),
        sa.Column("is_home", sa.Boolean(), nullable=True),
        sa.Column("minutes", sa.Float(), nullable=True),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("rebounds", sa.Integer(), nullable=True),
        sa.Column("assists", sa.Integer(), nullable=True),
        sa.Column("steals", sa.Integer(), nullable=True),
        sa.Column("blocks", sa.Integer(), nullable=True),
        sa.Column("turnovers", sa.Integer(), nullable=True),
        sa.Column("field_goals_made", sa.Integer(), nullable=True),
        sa.Column("field_goals_attempted", sa.Integer(), nullable=True),
        sa.Column("three_pointers_made", sa.Integer(), nullable=True),
        sa.Column("three_pointers_attempted", sa.Integer(), nullable=True),
        sa.Column("free_throws_made", sa.Integer(), nullable=True),
        sa.Column("free_throws_attempted", sa.Integer(), nullable=True),
        sa.Column("offensive_rebounds", sa.Integer(), nullable=True),
        sa.Column("defensive_rebounds", sa.Integer(), nullable=True),
        sa.Column("personal_fouls", sa.Integer(), nullable=True),
        sa.Column("plus_minus", sa.Integer(), nullable=True),
        sa.Column("fantasy_points", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["opponent_team_id"],
            ["teams.id"],
        ),
        sa.ForeignKeyConstraint(
            ["player_id"],
            ["players.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_player_game_stats_game_date"),
        "player_game_stats",
        ["game_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_player_game_stats_player_id"),
        "player_game_stats",
        ["player_id"],
        unique=False,
    )
    op.create_index(
        "ix_player_game_stats_player_date",
        "player_game_stats",
        ["player_id", "game_date"],
        unique=False,
    )

    # Create player_predictions table
    op.create_table(
        "player_predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("prediction_date", sa.Date(), nullable=False),
        sa.Column(
            "predictions", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=True),
        sa.Column(
            "factors", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("actual_stats", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["player_id"],
            ["players.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_player_predictions_prediction_date"),
        "player_predictions",
        ["prediction_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_player_predictions_player_id"),
        "player_predictions",
        ["player_id"],
        unique=False,
    )
    op.create_index(
        "ix_player_predictions_player_date",
        "player_predictions",
        ["player_id", "prediction_date"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_player_predictions_player_date", table_name="player_predictions")
    op.drop_index(
        op.f("ix_player_predictions_player_id"), table_name="player_predictions"
    )
    op.drop_index(
        op.f("ix_player_predictions_prediction_date"), table_name="player_predictions"
    )
    op.drop_table("player_predictions")

    op.drop_index("ix_player_game_stats_player_date", table_name="player_game_stats")
    op.drop_index(
        op.f("ix_player_game_stats_player_id"), table_name="player_game_stats"
    )
    op.drop_index(
        op.f("ix_player_game_stats_game_date"), table_name="player_game_stats"
    )
    op.drop_table("player_game_stats")

    op.drop_index(op.f("ix_players_team_id"), table_name="players")
    op.drop_index(op.f("ix_players_name"), table_name="players")
    op.drop_table("players")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_teams_abbreviation"), table_name="teams")
    op.drop_table("teams")

    op.execute("DROP TYPE injurystatus")
    op.execute("DROP TYPE usertier")
