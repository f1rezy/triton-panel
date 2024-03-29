"""Initial

Revision ID: bd8e366bffca
Revises: 
Create Date: 2023-09-07 00:46:12.211143

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bd8e366bffca'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('models',
    sa.Column('name', sa.VARCHAR(length=80), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__models')),
    sa.UniqueConstraint('id', name=op.f('uq__models__id'))
    )
    op.create_table('versions',
    sa.Column('name', sa.VARCHAR(length=80), nullable=False),
    sa.Column('model_id', sa.UUID(), nullable=False),
    sa.Column('upload_date', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['model_id'], ['models.id'], name=op.f('fk__versions__model_id__models')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__versions')),
    sa.UniqueConstraint('id', name=op.f('uq__versions__id'))
    )
    op.create_table('triton_loaded',
    sa.Column('version_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['version_id'], ['versions.id'], name=op.f('fk__triton_loaded__version_id__versions')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__triton_loaded')),
    sa.UniqueConstraint('id', name=op.f('uq__triton_loaded__id'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('triton_loaded')
    op.drop_table('versions')
    op.drop_table('models')
    # ### end Alembic commands ###
