"""initial

Revision ID: initial
Revises: 
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('invited_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_foreign_key(
        'users_invited_by_fkey',
        'users', 'users',
        ['invited_by'], ['id']
    )

    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('university', sa.String(), nullable=False),
        sa.Column('bio', sa.String(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_foreign_key(
        'profiles_user_id_fkey',
        'profiles', 'users',
        ['user_id'], ['id']
    )

    # Create interests table
    op.create_table(
        'interests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create user_interests association table
    op.create_table(
        'user_interests',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('interest_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['profiles.id'], ),
        sa.ForeignKeyConstraint(['interest_id'], ['interests.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'interest_id')
    )

    # Create invite_codes table
    op.create_table(
        'invite_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('used_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_foreign_key(
        'invite_codes_creator_id_fkey',
        'invite_codes', 'users',
        ['creator_id'], ['id']
    )
    op.create_foreign_key(
        'invite_codes_used_by_fkey',
        'invite_codes', 'users',
        ['used_by'], ['id']
    )

def downgrade() -> None:
    op.drop_table('invite_codes')
    op.drop_table('user_interests')
    op.drop_table('interests')
    op.drop_table('profiles')
    op.drop_table('users') 