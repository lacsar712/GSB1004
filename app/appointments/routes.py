from datetime import datetime

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from . import appointments_bp
from ..extensions import db
from ..models import Appointment, Package, User
from ..access import role_required
from ..time_utils import business_today


@appointments_bp.route("/")
@login_required
@role_required("admin", "staff", "user")
def list_appointments():
    if current_user.role in {"admin", "staff"}:
        appointments = Appointment.query.order_by(Appointment.scheduled_date.desc()).all()
    else:
        appointments = (
            Appointment.query.filter_by(user_id=current_user.id)
            .order_by(Appointment.scheduled_date.desc())
            .all()
        )
    return render_template("appointments/list.html", appointments=appointments)


@appointments_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff", "user")
def new_appointment():
    packages = Package.query.all()
    users = None
    if current_user.role in ["admin", "staff"]:
        users = User.query.filter_by(role="user").order_by(User.username).all()

    if request.method == "POST":
        package_id = request.form.get("package_id")
        scheduled_date = request.form.get("scheduled_date")
        scheduled_time = request.form.get("scheduled_time")
        user_id = request.form.get("user_id")

        if not all([package_id, scheduled_date, scheduled_time]):
            flash("请完整填写预约信息", "warning")
            return render_template("appointments/new.html", packages=packages, users=users)

        if current_user.role in ["admin", "staff"]:
            if not user_id:
                flash("请为预约选择一个用户", "warning")
                return render_template("appointments/new.html", packages=packages, users=users)

            try:
                target_user_id = int(user_id)
            except (TypeError, ValueError):
                flash("预约用户参数无效", "warning")
                return render_template("appointments/new.html", packages=packages, users=users)

            target_user = db.session.get(User, target_user_id)
            if not target_user or target_user.role != "user":
                flash("只能为普通用户创建预约", "warning")
                return render_template("appointments/new.html", packages=packages, users=users)

        try:
            date_value = datetime.strptime(scheduled_date, "%Y-%m-%d").date()
            time_value = datetime.strptime(scheduled_time, "%H:%M").time()

            # 验证日期必须是今天及以后
            if date_value < business_today():
                flash("预约日期必须是今天或之后的日期", "warning")
                return render_template("appointments/new.html", packages=packages, users=users)
        except ValueError:
            flash("日期或时间格式不正确", "danger")
            return render_template("appointments/new.html", packages=packages, users=users)

        conflict = Appointment.query.filter_by(
            scheduled_date=date_value, scheduled_time=time_value
        ).first()
        if conflict:
            flash("该时段已被预约，请选择其他时间", "danger")
            return render_template("appointments/new.html", packages=packages, users=users)

        target_user_id = target_user_id if current_user.role in ["admin", "staff"] else current_user.id

        appointment = Appointment(
            user_id=target_user_id,
            package_id=int(package_id),
            scheduled_date=date_value,
            scheduled_time=time_value,
        )
        db.session.add(appointment)
        db.session.commit()
        flash("预约已成功提交", "success")
        return redirect(url_for("appointments.list_appointments"))

    return render_template("appointments/new.html", packages=packages, users=users)
