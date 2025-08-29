"""Add patient data and collection phase to sessions

Revision ID: 71f8e48123c4
Revises: 
Create Date: 2025-08-29 07:17:19.002251

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71f8e48123c4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tables if they don't exist
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('current_assessment', sa.JSON, nullable=True),
        sa.Column('openai_thread_id', sa.String(255), nullable=True),
        sa.Column('patient_data', sa.JSON, nullable=True),
        sa.Column('is_collecting_data', sa.Boolean, default=True),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )
    
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.String(36), primary_key=True, index=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('chat_sessions.id'), nullable=False, index=True),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )


def downgrade() -> None:
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')