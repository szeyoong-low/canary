from typing import Annotated

from fastapi import Query

from ..constants import MetricGroup

type SetQueryParam = Annotated[set[str], Query()]


DISPLAY_PATH_PARAM: str = "{display}"


def _get_terminal_path(metric_group: MetricGroup) -> str:
    return f"/{metric_group}/{DISPLAY_PATH_PARAM}"
