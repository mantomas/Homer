"""add Page

Revision ID: 9767077fab13
Revises: f40db34b1b89
Create Date: 2025-01-04 16:41:06.616798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9767077fab13'
down_revision = 'f40db34b1b89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('page',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=140), nullable=False),
    sa.Column('url_suffix', sa.String(length=30), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('body_html', sa.Text(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('last_edited', sa.DateTime(), nullable=False),
    sa.Column('last_edit_by', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['last_edit_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('url_suffix')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('page')
    # ### end Alembic commands ###
