"""rename template filters to stat groups

Revision ID: f64c337245b7
Revises: 1daa0e0db3c3
Create Date: 2026-11-26 15:58:46.275302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f64c337245b7'
down_revision: Union[str, Sequence[str], None] = '1daa0e0db3c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("template", "filters", new_column_name="stat_groups")
    # A template's mod filters become one "and" group.
    op.execute(
        "UPDATE template SET stat_groups = jsonb_build_array("
        "jsonb_build_object('type', 'and', 'mod_filters', stat_groups)) "
        "WHERE stat_groups <> '[]'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # The mod filters of all groups go back into one list; the group types are lost.
    op.execute(
        "UPDATE template SET stat_groups = "
        "jsonb_path_query_array(stat_groups, '$[*].mod_filters[*]')"
    )
    op.alter_column("template", "stat_groups", new_column_name="filters")