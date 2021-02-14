"""empty message

Revision ID: 422f8cf22701
Revises: 1bf93ded29ee
Create Date: 2021-02-13 12:53:26.463390

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '422f8cf22701'
down_revision = '1bf93ded29ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
