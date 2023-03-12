"""Add created_at column to tokens table

Revision ID: f4a2dad07ceb
Revises: afecfc63753e
Create Date: 2023-03-09 20:11:56.445450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4a2dad07ceb'
down_revision = 'afecfc63753e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tokens', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tokens', 'created_at')
    # ### end Alembic commands ###
