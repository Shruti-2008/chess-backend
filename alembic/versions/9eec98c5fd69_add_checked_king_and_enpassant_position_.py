"""Add checked_king and enpassant_position columns. Rename column win_reason to end_reason and make it int.

Revision ID: 9eec98c5fd69
Revises: f6b86df47b1e
Create Date: 2023-02-16 12:00:29.345817

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9eec98c5fd69'
down_revision = 'f6b86df47b1e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
