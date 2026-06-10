import re


MISSING_MARKERS = {"", "n/a", "na", "-", "--", "none", "null"}
BLOOD_PRESSURE_PATTERN = re.compile(r"^\d+(?:\.\d+)?(?:/\d+(?:\.\d+)?)?$")


def parse_normal_range(range_text):
    if not range_text:
        return None, None

    range_text = str(range_text).strip()
    matched = re.match(r"^\s*(\d+(?:\.\d+)?)\s*[-~～]\s*(\d+(?:\.\d+)?)\s*$", range_text)
    if matched:
        try:
            min_val = float(matched.group(1))
            max_val = float(matched.group(2))
        except (TypeError, ValueError):
            return None, None
        if min_val > max_val:
            min_val, max_val = max_val, min_val
        return min_val, max_val

    values = re.findall(r"\d+(?:\.\d+)?", range_text)
    if len(values) < 2:
        return None, None

    try:
        min_val = float(values[0])
        max_val = float(values[1])
    except (TypeError, ValueError):
        return None, None

    if min_val > max_val:
        min_val, max_val = max_val, min_val

    return min_val, max_val


def is_missing_value(raw_value):
    normalized = str(raw_value or "").strip().lower()
    return normalized in MISSING_MARKERS


def parse_metric_numeric(metric_name, raw_value):
    value_text = str(raw_value or "").strip()
    if not value_text:
        return None, None

    if metric_name == "血压":
        normalized = value_text.replace("／", "/")
        if not BLOOD_PRESSURE_PATTERN.match(normalized):
            return None, None

        if "/" in normalized:
            systolic_text = normalized.split("/", 1)[0].strip()
            try:
                return float(systolic_text), f"图表取收缩压 {systolic_text}"
            except (TypeError, ValueError):
                return None, None

        try:
            return float(normalized), None
        except (TypeError, ValueError):
            return None, None

    try:
        return float(value_text), None
    except (TypeError, ValueError):
        return None, None


def build_metric_status(metric_name, raw_value, normal_range):
    raw_text = str(raw_value or "").strip()
    min_val, max_val = parse_normal_range(normal_range)
    has_range = min_val is not None and max_val is not None
    marker_missing = is_missing_value(raw_text)
    numeric_value, chart_note = parse_metric_numeric(metric_name, raw_text)
    invalid_numeric = (not marker_missing) and (numeric_value is None)
    is_missing = marker_missing or invalid_numeric

    display_value = "未录入" if marker_missing else (raw_text or "未录入")
    is_abnormal = False
    status = "missing"

    if is_missing:
        status = "missing"
    elif not has_range:
        status = "no_range"
    elif numeric_value is not None and (numeric_value < min_val or numeric_value > max_val):
        is_abnormal = True
        status = "abnormal"
    else:
        status = "normal"

    return {
        "display_value": display_value,
        "chart_value": numeric_value if numeric_value is not None else 0.0,
        "is_numeric": numeric_value is not None,
        "is_missing": is_missing,
        "is_abnormal": is_abnormal,
        "status": status,
        "min": min_val,
        "max": max_val,
        "has_range": has_range,
        "chart_note": chart_note,
    }
