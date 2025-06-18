"""Payments Schema

Revision ID: a4235c10f8fa
Revises: 
Create Date: 2025-06-15 19:06:46.591784

"""

# revision identifiers, used by Alembic.
revision = 'a4235c10f8fa'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'payment',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('requester_type', sa.Integer(), nullable=False),
        sa.Column('requester_id', sa.Integer(), nullable=False),
        sa.Column('secondary_requester_id', sa.Integer(), nullable=True),
        
        sa.Column('payment_method', sa.Enum('tunai', 'bca_va', 'qris', 'gopay', 'ovo',name='payment_method_enum'), nullable=False),
        sa.Column('payment_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False, server_default='1'),
        
        sa.Column('psp_id', sa.String(), nullable=True),
        sa.Column('raw_response', JSONB(), nullable=True),
        
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('settle_date', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('payment')