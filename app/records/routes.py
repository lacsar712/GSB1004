from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from . import records_bp
from ..access import role_required
from ..extensions import db
from ..metric_utils import BLOOD_PRESSURE_PATTERN
from ..models import Appointment, MetricDefinition, MetricRecord
from ..time_utils import business_today


@records_bp.route("/")
@login_required
@role_required("staff", "admin")
def list_records():
    appointments = Appointment.query.order_by(Appointment.scheduled_date.desc()).all()
    return render_template("records/list.html", appointments=appointments, today=business_today())


@records_bp.route("/<int:appointment_id>", methods=["GET", "POST"])
@login_required
@role_required("staff", "admin")
def new_record(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    # 防止提前录入
    if appointment.scheduled_date > business_today():
        flash("无法为未来的预约录入数据", "warning")
        return redirect(url_for("records.list_records"))

    all_metrics = MetricDefinition.query.order_by(MetricDefinition.category, MetricDefinition.id).all()

    grouped_metrics = {}
    for metric in all_metrics:
        if metric.category not in grouped_metrics:
            grouped_metrics[metric.category] = []
        grouped_metrics[metric.category].append(metric)

    if request.method == "POST":
        def upsert_metric_records():
            for metric in all_metrics:
                value = request.form.get(f"metric_{metric.id}", "").strip()
                if metric.name == "血压":
                    value = value.replace("／", "/")
                record = MetricRecord.query.filter_by(
                    appointment_id=appointment.id, metric_definition_id=metric.id
                ).first()
                if record:
                    record.value = value
                    record.recorded_by_id = current_user.id
                else:
                    record = MetricRecord(
                        appointment_id=appointment.id,
                        metric_definition_id=metric.id,
                        value=value,
                        recorded_by_id=current_user.id,
                    )
                    db.session.add(record)
            appointment.status = "completed"

        for metric in all_metrics:
            value = request.form.get(f"metric_{metric.id}", "").strip()
            if not value:
                flash("请填写完整的指标数据", "warning")
                return render_template(
                    "records/new.html",
                    appointment=appointment,
                    grouped_metrics=grouped_metrics,
                    total_metrics=len(all_metrics)
                )
            if metric.name == "血压":
                normalized = value.replace("／", "/")
                if not BLOOD_PRESSURE_PATTERN.match(normalized):
                    flash("血压格式不正确，请输入如 120 或 120/80", "warning")
                    return render_template(
                        "records/new.html",
                        appointment=appointment,
                        grouped_metrics=grouped_metrics,
                        total_metrics=len(all_metrics)
                    )

        upsert_metric_records()
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            upsert_metric_records()
            db.session.commit()

        flash("体检数据已保存", "success")
        return redirect(url_for("records.list_records"))

    return render_template(
        "records/new.html",
        appointment=appointment,
        grouped_metrics=grouped_metrics,
        total_metrics=len(all_metrics)
    )
