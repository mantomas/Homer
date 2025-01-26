"""New ToDo table

Revision ID: 7673ee574a24
Revises: 4842138b56c6
Create Date: 2025-01-26 19:28:24.316015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7673ee574a24'
down_revision = '4842138b56c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('to_do',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('last_edited', sa.DateTime(), nullable=False),
    sa.Column('last_edit_by', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=140), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('body_html', sa.Text(), nullable=False),
    sa.Column('due_date', sa.DateTime(), nullable=False),
    sa.Column('done', sa.Boolean(), nullable=False),
    sa.Column('done_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['last_edit_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('to_do')
    # ### end Alembic commands ###
