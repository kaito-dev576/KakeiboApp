"""Initial database schema

Revision ID: 216d71660c6c
Revises: 
Create Date: 2026-08-13 19:22:42.965591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '216d71660c6c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 公開済み環境に同じテーブルがある場合は、既存データを残して
    # Alembicの管理だけを開始できるようにする。
    existing_tables = set(sa.inspect(op.get_bind()).get_table_names())

    if 'user' not in existing_tables:
        op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    if 'budget' not in existing_tables:
        op.create_table('budget',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('month', sa.Integer(), nullable=False),
    sa.Column('budget', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'year', 'month', name='unique_user_month_budget')
    )
    if 'category' not in existing_tables:
        op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('icon', sa.String(length=10), nullable=False),
    sa.Column('type', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'name', name='unique_user_category')
    )
    if 'expense' not in existing_tables:
        op.create_table('expense',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=10), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('memo', sa.String(length=200), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    existing_tables = set(sa.inspect(op.get_bind()).get_table_names())
    for table_name in ('expense', 'category', 'budget', 'user'):
        if table_name in existing_tables:
            op.drop_table(table_name)
