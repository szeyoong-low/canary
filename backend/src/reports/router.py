from fastapi import APIRouter

router = APIRouter(prefix="/reports")

REPORT_ID_PATH_PARAM_SEGMENT = "/{report_id}"


@router.post("/")
def create_new_report():
    return "create_new_report"


@router.get("/previews")
def get_report_previews():
    return "get_report_previews"


@router.get(REPORT_ID_PATH_PARAM_SEGMENT)
def get_specific_report():
    return "get_specific_report"


@router.patch(REPORT_ID_PATH_PARAM_SEGMENT)
def update_report_metadata():
    return "update_report_metadata"


@router.post(f"{REPORT_ID_PATH_PARAM_SEGMENT}/contents")
def add_generated_content_to_report():
    return "add_generated_content_to_report"
