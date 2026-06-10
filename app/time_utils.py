import os
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import current_app, has_app_context


DEFAULT_TIMEZONE = "Asia/Shanghai"


def _business_tz():
    if has_app_context():
        tz_name = current_app.config.get(
            "APP_TIMEZONE", os.environ.get("APP_TIMEZONE", DEFAULT_TIMEZONE)
        )
    else:
        tz_name = os.environ.get("APP_TIMEZONE", DEFAULT_TIMEZONE)
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return ZoneInfo(DEFAULT_TIMEZONE)


def business_now():
    return datetime.now(_business_tz())


def business_today():
    return business_now().date()
