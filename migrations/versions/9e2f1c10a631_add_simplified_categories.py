"""Add simplified categories

Revision ID: 9e2f1c10a631
Revises: 216d71660c6c
"""
from alembic import op
import sqlalchemy as sa


revision = "9e2f1c10a631"
down_revision = "216d71660c6c"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    users = connection.execute(sa.text('SELECT id FROM "user"')).fetchall()

    desired_categories = (
        ("給与", "💰", "収入"),
        ("遊び", "🎮", "支出"),
        ("自己投資", "📚", "支出"),
    )

    for user in users:
        for name, icon, category_type in desired_categories:
            exists = connection.execute(
                sa.text(
                    "SELECT 1 FROM category "
                    "WHERE user_id = :user_id AND name = :name"
                ),
                {"user_id": user.id, "name": name},
            ).first()

            if not exists:
                connection.execute(
                    sa.text(
                        "INSERT INTO category (user_id, name, icon, type) "
                        "VALUES (:user_id, :name, :icon, :type)"
                    ),
                    {
                        "user_id": user.id,
                        "name": name,
                        "icon": icon,
                        "type": category_type,
                    },
                )


def downgrade():
    # 過去の取引で使われる可能性があるため、カテゴリーは削除しない。
    pass
