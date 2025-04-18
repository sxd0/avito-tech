"""Initial migration

Revision ID: 6a0a1c925813
Revises: 
Create Date: 2025-04-18 12:29:03.975287

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a0a1c925813'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pvzs',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('registration_date', sa.DateTime(), nullable=True),
    sa.Column('city', sa.Enum('Москва', 'Санкт-Петербург', 'Казань', name='city_type'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=True),
    sa.Column('role', sa.Enum('employee', 'moderator', name='user_role'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('receptions',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('date_time', sa.DateTime(), nullable=True),
    sa.Column('pvz_id', sa.String(), nullable=True),
    sa.Column('status', sa.Enum('in_progress', 'close', name='reception_status'), nullable=True),
    sa.ForeignKeyConstraint(['pvz_id'], ['pvzs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('date_time', sa.DateTime(), nullable=True),
    sa.Column('type', sa.Enum('электроника', 'одежда', 'обувь', name='product_type'), nullable=True),
    sa.Column('reception_id', sa.String(), nullable=True),
    sa.Column('order_in_reception', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['reception_id'], ['receptions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('products')
    op.drop_table('receptions')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('pvzs')
    # ### end Alembic commands ###
