from ..constants import MetricGroup

DISPLAY_PATH_PARAM: str = "{display}"


def _get_terminal_path(metric_group: MetricGroup) -> str:
    return f"/{metric_group}/{DISPLAY_PATH_PARAM}"
