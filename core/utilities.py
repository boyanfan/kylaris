from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta

def datatime_to_seconds(time: datetime) -> int:
    """Convert UTC datatime to seconds representation."""
    return int(time.timestamp())

def datatime_to_milliseconds(time: datetime) -> int:
    """Convert UTC datatime to milliseconds representation."""
    return datatime_to_seconds(time) * 1000

def milliseconds_to_datatime(milliseconds: int) -> datetime:
    """Convert milliseconds to UTC datatime."""
    return datetime.fromtimestamp(milliseconds / 1000.0, tz=timezone.utc)

def datatime_now() -> datetime:
    """Get the current UTC datetime."""
    return datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)

def datetime_from_past(*, hours: int = 0, days: int = 0, months: int = 0, years: int = 0) -> datetime:
    """Get a UTC datetime representing a point in the past by a specified offset."""
    return datatime_now() - timedelta(hours=hours, days=days) - relativedelta(months=months, years=years)
