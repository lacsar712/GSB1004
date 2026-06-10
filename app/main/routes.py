from flask import render_template
from flask_login import login_required, current_user

from . import main_bp
from ..models import Appointment


@main_bp.route("/")
@login_required
def index():
    if current_user.role in {"admin", "staff"}:
        appointment_count = Appointment.query.count()
        completed_exam_count = Appointment.query.filter_by(status="completed").count()
    else:
        appointment_count = Appointment.query.filter_by(user_id=current_user.id).count()
        completed_exam_count = (
            Appointment.query.filter_by(user_id=current_user.id, status="completed")
            .count()
        )

    return render_template(
        "main/index.html",
        appointment_count=appointment_count,
        completed_exam_count=completed_exam_count,
    )
