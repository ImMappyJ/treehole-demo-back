"""empty message

Revision ID: 66c438dadc9e
Revises: ea02eec0bb35
Create Date: 2024-02-29 15:17:47.763272

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '66c438dadc9e'
down_revision = 'ea02eec0bb35'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('db_logger', schema=None) as batch_op:
        batch_op.add_column(sa.Column('info', sa.String(length=100), nullable=True))

    with op.batch_alter_table('db_post_articles', schema=None) as batch_op:
        batch_op.alter_column('context',
               existing_type=mysql.MEDIUMTEXT(),
               type_=sa.Text(length=65536),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('db_post_articles', schema=None) as batch_op:
        batch_op.alter_column('context',
               existing_type=sa.Text(length=65536),
               type_=mysql.MEDIUMTEXT(),
               existing_nullable=False)

    with op.batch_alter_table('db_logger', schema=None) as batch_op:
        batch_op.drop_column('info')

    # ### end Alembic commands ###