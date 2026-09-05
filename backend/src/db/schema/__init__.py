from sqlalchemy import MetaData

"""
The single `MetaData` every table binds to, and the source of truth autogenerate
diffs the live database against.
"""

# https://alembic.sqlalchemy.org/en/latest/naming.html
#
# `column_0_N_name` concatenates all columns in the constraint, unlike the
# `column_0_name` shown in the Alembic docs. The ledger tables have composite
# keys, and the single-column form would give two different constraints on one
# table the same name.
#
# Note: Postgres truncates identifiers at 63 bytes.
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    # Interpolates `name=` passed to CheckConstraint, which is therefore mandatory
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata: MetaData = MetaData(naming_convention=NAMING_CONVENTION)

# Imported for its side effect: a `Table` registers itself against the MetaData
# only when its module is executed. Without this, `target_metadata` reaches
# autogenerate empty and every existing table looks like one to drop.
#
# It sits at the bottom because `identity` imports `metadata` from here, so the
# name has to exist before that module runs.
from . import app_users  # noqa: F401
