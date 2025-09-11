import humanize


def human_date(dt) -> str:
    return dt.strftime("%A, %B %d, %Y")


def human_time(dt) -> str:
    return dt.strftime("%I:%M %p")


def human_datetime(dt) -> str:
    return dt.strftime("%A, %B %d, %Y %I:%M %p")


def human_delta(seconds: int) -> str:
    """Return uptime as string."""
    delta = humanize.precisedelta(seconds)
    return delta.split(" and ")[0]
