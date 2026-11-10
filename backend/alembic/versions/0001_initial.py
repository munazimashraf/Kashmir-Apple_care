from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table("users", sa.Column("id", uuid, primary_key=True), sa.Column("email", sa.String(320), nullable=False, unique=True), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("preferred_language", sa.String(8), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("orchards", sa.Column("id", uuid, primary_key=True), sa.Column("owner_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("latitude", sa.Float, nullable=False), sa.Column("longitude", sa.Float, nullable=False), sa.Column("district", sa.String(80)))
    op.create_index("ix_orchards_owner_id", "orchards", ["owner_id"])
    op.create_table("diagnoses", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("orchard_id", uuid, sa.ForeignKey("orchards.id", ondelete="SET NULL")), sa.Column("disease", sa.String(80), nullable=False), sa.Column("confidence", sa.Float, nullable=False), sa.Column("growth_stage", sa.String(40), nullable=False), sa.Column("image_sha256", sa.String(64), nullable=False), sa.Column("heatmap", postgresql.JSONB, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_diagnoses_user_id", "diagnoses", ["user_id"])
    op.create_index("ix_diagnoses_disease", "diagnoses", ["disease"])
    op.create_index("ix_diagnoses_image_sha256", "diagnoses", ["image_sha256"])
    op.create_table("spray_logs", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("orchard_id", uuid, sa.ForeignKey("orchards.id", ondelete="SET NULL")), sa.Column("product", sa.String(160), nullable=False), sa.Column("dosage", sa.String(120), nullable=False), sa.Column("sprayed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("notes", sa.Text))
    op.create_index("ix_spray_logs_user_id", "spray_logs", ["user_id"])
    op.create_table("weather_history", sa.Column("id", sa.Integer, primary_key=True), sa.Column("orchard_id", uuid, sa.ForeignKey("orchards.id", ondelete="CASCADE"), nullable=False), sa.Column("observed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("provider", sa.String(40), nullable=False), sa.Column("payload", postgresql.JSONB, nullable=False))
    op.create_index("ix_weather_history_orchard_id", "weather_history", ["orchard_id"])


def downgrade() -> None:
    op.drop_table("weather_history")
    op.drop_table("spray_logs")
    op.drop_table("diagnoses")
    op.drop_table("orchards")
    op.drop_table("users")
