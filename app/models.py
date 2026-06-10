from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    appointments = db.relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    records = db.relationship("MetricRecord", back_populates="recorded_by")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)

    appointments = db.relationship("Appointment", back_populates="package", cascade="all, delete-orphan")


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey("package.id"), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)
    scheduled_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="scheduled")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="appointments")
    package = db.relationship("Package", back_populates="appointments")
    metric_records = db.relationship("MetricRecord", back_populates="appointment", cascade="all, delete-orphan")

    def scheduled_datetime(self):
        return datetime.combine(self.scheduled_date, self.scheduled_time)


class MetricDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    unit = db.Column(db.String(16), nullable=False)
    normal_range = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(64), nullable=False, default="基本指标")
    suggestion = db.Column(db.String(256), nullable=True)

    metric_records = db.relationship("MetricRecord", back_populates="metric_definition")


class MetricRecord(db.Model):
    __table_args__ = (
        db.UniqueConstraint(
            "appointment_id",
            "metric_definition_id",
            name="uq_metric_record_appointment_metric",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"), nullable=False)
    metric_definition_id = db.Column(db.Integer, db.ForeignKey("metric_definition.id"), nullable=False)
    value = db.Column(db.String(120), nullable=False)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    appointment = db.relationship("Appointment", back_populates="metric_records")
    metric_definition = db.relationship("MetricDefinition", back_populates="metric_records")
    recorded_by = db.relationship("User", back_populates="records")
