from datetime import date


def validate_date_range(start: date, end: date) -> None:
    if start > end:
        raise ValueError("Start date must be at or before end date")
