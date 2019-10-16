"""empty message

Revision ID: cb27366d230b
Revises: 10b4cf0ae3eb
Create Date: 2019-09-26 23:28:27.530928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb27366d230b'
down_revision = '10b4cf0ae3eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('adminlog',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.Column('operate', sa.String(length=300), nullable=True),
    sa.Column('ip', sa.String(length=100), nullable=True),
    sa.Column('add_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['user.uid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_adminlog_add_time'), 'adminlog', ['add_time'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_adminlog_add_time'), table_name='adminlog')
    op.drop_table('adminlog')
    # ### end Alembic commands ###