"""
utils.py
--------
Small helper functions shared across Tkinter UI files.
"""

def split_due_date(due_date: str) -> tuple[str, str]:
    """
    Convert ISO 'YYYY-MM-DDTHH:MM' → ('YYYY-MM-DD', 'HH:MM').

    Returns empty strings if the input is missing or malformed.
    """
    if not due_date:
        return ("", "")

    if "T" not in due_date:
        return ("", "")

    date, time = due_date.split("T", 1)
    return (date, time)


def build_due_date(date: str, time: str) -> str:
    """
    Build ISO timestamp from separate date + time fields.

    Does not validate the values — validation happens in the connector/UI.
    """
    return f"{date}T{time}"
