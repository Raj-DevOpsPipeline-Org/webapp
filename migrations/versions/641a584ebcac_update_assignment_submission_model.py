"""update Assignment Submission model

Revision ID: 641a584ebcac
Revises: ebfe945b0239
Create Date: 2023-11-29 02:01:17.270786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '641a584ebcac'
down_revision = 'ebfe945b0239'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignment_submission', schema=None) as batch_op:
        batch_op.add_column(sa.Column('submission_updated', sa.DateTime(), nullable=False))
        batch_op.create_unique_constraint(None, ['id'])
        batch_op.drop_constraint('assignment_submission_account_id_fkey', type_='foreignkey')
        batch_op.drop_column('account_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignment_submission', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_id', sa.UUID(), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('assignment_submission_account_id_fkey', 'account', ['account_id'], ['id'])
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('submission_updated')

    # ### end Alembic commands ###
