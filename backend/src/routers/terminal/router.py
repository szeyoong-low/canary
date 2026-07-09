from fastapi import APIRouter


TERMINAL_PREFIX = "/terminal"
router = APIRouter(prefix=TERMINAL_PREFIX)

# Path parameters
METRIC_PATH_PARAM = "/{metric}"
DISPLAY_PATH_PARAM = "/{display}"
TERMINAL_PATH = f"{METRIC_PATH_PARAM}{DISPLAY_PATH_PARAM}"

router = APIRouter(prefix=TERMINAL_PREFIX)


@router.get(TERMINAL_PATH)
def terminal_path_op(metric: str, display: str):
    return {"metric": metric, "display": display}
