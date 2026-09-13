"""Structured logging: every log line is one JSON object on stdout."""

import json
import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

type Level = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Key under which `log` stashes its fields on the LogRecord. They travel in one
# nested dict because `extra=` assigns its keys directly onto the record, and a
# key that collides with a built-in attribute (`message`, `module`, `args`) makes
# logging raise.
_FIELDS = "canary_fields"

# Named, so that third-party records can be told apart from ours by logger name.
_logger = logging.getLogger("canary")


class JsonFormatter(logging.Formatter):
    """Renders a record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        # Insertion order is preserved in the output, so the fields every line
        # shares come first and the variable ones trail.
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            # Where it was logged from. Correct for our own calls because `log`
            # passes `stacklevel=2`.
            "source": f"{record.module}:{record.lineno}",
        }

        fields: dict[str, Any] | None = getattr(record, _FIELDS, None)

        if fields is None:
            # A record from uvicorn, SQLAlchemy or LangChain. It has no event
            # name, so the logger's name stands in as a coarse one and the
            # interpolated message goes in whole.
            payload["event"] = record.name
            payload["message"] = record.getMessage()
        else:
            payload.update(fields)

        if record.exc_info:
            payload["traceback"] = self.formatException(record.exc_info)

        # `default=str` so that a UUID, a datetime or a Pydantic model passed as
        # a detail is stringified rather than raising.
        return json.dumps(payload, default=str)


def setup_logging(level: Level | None = None) -> None:
    """
    Install the JSON formatter process-wide. Call once, at startup.

    Falls back to the `LOG_LEVEL` environment variable, then INFO.
    """

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root: logging.Logger = logging.getLogger()
    # Replaced rather than added to, so nothing is emitted twice in the old
    # unstructured format alongside the new one.
    root.handlers = [handler]
    root.setLevel(level or os.getenv("LOG_LEVEL", "INFO"))

    # uvicorn installs handlers on its own loggers and stops them propagating,
    # which would leave its lines in a second format. Clearing them sends those
    # records up to the root handler above instead.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger: logging.Logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True


def log(
    level: Level,
    event: str,
    *,
    user_id: UUID | str | None = None,
    report_id: UUID | str | None = None,
    error: BaseException | None = None,
    **details: Any,
) -> None:
    """
    Emit one structured line.

    `event` is a stable, greppable identifier (`"report.created"`), never a
    sentence: filters are written against it, so it must not vary per call. Put
    the varying parts in `details`.

    `user_id` and `report_id` are named because they are the correlation keys a
    log explorer gets filtered by. Passing `error` attaches its traceback.
    """

    fields: dict[str, Any] = {"event": event}

    if user_id is not None:
        fields["user_id"] = user_id

    if report_id is not None:
        fields["report_id"] = report_id

    if details:
        fields["details"] = details

    _logger.log(
        logging.getLevelNamesMapping()[level],
        event,  # Unused by JsonFormatter. The message any other formatter reads
        extra={_FIELDS: fields},
        exc_info=error,
        stacklevel=2,  # Points the record at our caller, not at this line.
    )
