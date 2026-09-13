from sqlalchemy import MetaData, func
from sqlalchemy.sql.elements import ColumnElement

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


def write_timestamp() -> ColumnElement:
    """The server default for any column recording when a row was written.

    `clock_timestamp()` rather than `now()`. `now()` is transaction START time
    and is constant for the whole transaction, so every row written in one
    transaction shares a timestamp to the microsecond. The ledger tables key on
    `(subject, set_at)`, which makes that a primary key collision: two writes to
    one report's history in a single transaction are simply impossible.
    `clock_timestamp()` advances as the statement runs, so they differ.

    Note the limit of this. Neither function reflects COMMIT order: a row is
    stamped before its transaction commits, so a long transaction can leave a
    timestamp earlier than one that started later and committed first. Reading
    the current value with `ORDER BY set_at DESC LIMIT 1` can therefore still
    name a stale row. `clock_timestamp()` narrows that window rather than
    closing it, and closing it properly needs a sequence.
    https://www.postgresql.org/docs/current/functions-datetime.html#FUNCTIONS-DATETIME-CURRENT

    A function, not a constant, so each column is given its own expression
    rather than eleven of them sharing one clause element.

    Kept here because `compare_server_default` is off in `migrations/env.py`:
    autogenerate will never notice this default drifting, so the one thing
    protecting it is that there is only one place to change.
    """

    return func.clock_timestamp()


# Imported for its side effect: a `Table` registers itself against the MetaData
# only when its module is executed. Without this, `target_metadata` reaches
# autogenerate empty and every existing table looks like one to drop.
#
# It sits at the bottom because they import `metadata` from here, so the
# name has to exist before that module runs.
from . import app_users, content, reports  # noqa: F401
