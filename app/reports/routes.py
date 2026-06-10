import json

from flask import render_template
from flask_login import login_required, current_user

from . import reports_bp
from ..metric_utils import build_metric_status
from ..models import Appointment, MetricDefinition, MetricRecord


@reports_bp.route("/")
@login_required
def list_reports():
    if current_user.role in {"admin", "staff"}:
        appointments = Appointment.query.order_by(Appointment.scheduled_date.desc()).all()
    else:
        appointments = (
            Appointment.query.filter_by(user_id=current_user.id)
            .order_by(Appointment.scheduled_date.desc())
            .all()
        )

    return render_template("reports/list.html", appointments=appointments)


@reports_bp.route("/<int:appointment_id>")
@login_required
def report_detail(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if current_user.role == "user" and appointment.user_id != current_user.id:
        return render_template("reports/unauthorized.html"), 403

    metric_definitions = MetricDefinition.query.order_by(
        MetricDefinition.category, MetricDefinition.id
    ).all()
    records = MetricRecord.query.filter_by(appointment_id=appointment.id).all()
    record_map = {record.metric_definition_id: record for record in records}

    chart_items = []
    health_suggestions = []
    suggestion_names = set()

    for metric in metric_definitions:
        record = record_map.get(metric.id)
        raw_value = record.value if record else ""
        status_data = build_metric_status(metric.name, raw_value, metric.normal_range)

        item = {
            "name": metric.name,
            "unit": metric.unit,
            "normal_range": metric.normal_range,
            "display_value": status_data["display_value"],
            "chart_value": status_data["chart_value"],
            "is_numeric": status_data["is_numeric"],
            "is_missing": status_data["is_missing"],
            "is_abnormal": status_data["is_abnormal"],
            "status": status_data["status"],
            "min": status_data["min"],
            "max": status_data["max"],
            "has_range": status_data["has_range"],
            "chart_note": status_data["chart_note"],
        }
        chart_items.append(item)

        if (
            status_data["status"] == "abnormal"
            and metric.suggestion
            and metric.name not in suggestion_names
        ):
            health_suggestions.append({"name": metric.name, "suggestion": metric.suggestion})
            suggestion_names.add(metric.name)

    total_metrics_count = len(chart_items)
    missing_metrics_count = sum(1 for item in chart_items if item["status"] == "missing")
    abnormal_records_count = sum(1 for item in chart_items if item["status"] == "abnormal")
    normal_records_count = sum(1 for item in chart_items if item["status"] == "normal")
    recorded_metrics_count = total_metrics_count - missing_metrics_count
    abnormal_denominator = abnormal_records_count + normal_records_count
    abnormal_rate = (
        round((abnormal_records_count / abnormal_denominator) * 100, 1)
        if abnormal_denominator
        else 0
    )

    return render_template(
        "reports/detail.html",
        appointment=appointment,
        records=records,
        chart_items=chart_items,
        chart_items_json=json.dumps(chart_items, ensure_ascii=False),
        total_metrics_count=total_metrics_count,
        recorded_metrics_count=recorded_metrics_count,
        missing_metrics_count=missing_metrics_count,
        normal_records_count=normal_records_count,
        abnormal_records_count=abnormal_records_count,
        abnormal_rate=abnormal_rate,
        health_suggestions=health_suggestions,
    )
