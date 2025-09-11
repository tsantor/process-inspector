import datetime
import sys

import humanize


def format_date(dt, format_string):
    if sys.platform == "win32":
        format_string = format_string.replace("%-", "%#")
    return dt.strftime(format_string)


def human_date(dt) -> str:
    return format_date(dt, "%A, %B %-d, %Y")


def human_date_short(dt) -> str:
    return format_date(dt, "%a, %b %-d, %Y")


def human_time(dt) -> str:
    time_string = format_date(dt, "%I:%M %p")
    # Remove leading zero from hour on all platforms
    return time_string.lstrip("0") if time_string[0] == "0" else time_string


def human_datetime(dt) -> str:
    return f"{human_date(dt)} {human_time(dt)}"


def human_datetime_short(dt) -> str:
    return f"{human_date_short(dt)} {human_time(dt)}"


def human_delta(seconds: int) -> str:
    """Return uptime as string."""
    delta = humanize.precisedelta(seconds)
    return delta.split(" and ")[0]
