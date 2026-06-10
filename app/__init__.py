import os

from flask import Flask, request
from sqlalchemy.exc import IntegrityError

from .db_maintenance import ensure_metric_record_unique_constraint
from .extensions import db, login_manager
from .models import User, Package, MetricDefinition


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.Config")
    app.config["APP_TIMEZONE"] = os.environ.get(
        "APP_TIMEZONE", app.config.get("APP_TIMEZONE", "Asia/Shanghai")
    )

    instance_dir = app.config.get("INSTANCE_DIR") or app.instance_path
    app.config["INSTANCE_DIR"] = instance_dir
    os.makedirs(instance_dir, exist_ok=True)

    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:///"):
        db_path = db_uri.replace("sqlite:///", "", 1)
        if not os.path.isabs(db_path):
            db_path = os.path.join(instance_dir, db_path)
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
        db_dir = os.path.dirname(db_path)
        try:
            os.makedirs(db_dir, exist_ok=True)
        except OSError:
            fallback_path = os.path.join(app.instance_path, "health.db")
            os.makedirs(app.instance_path, exist_ok=True)
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{fallback_path}"

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "请先登录后再访问该页面。"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_navigation_context():
        endpoint = request.endpoint or ""
        if endpoint.startswith("appointments."):
            active_nav = "appointments"
        elif endpoint.startswith("records."):
            active_nav = "records"
        elif endpoint.startswith("reports."):
            active_nav = "reports"
        else:
            active_nav = None

        return {"active_nav": active_nav, "active_endpoint": endpoint}

    from .auth.routes import auth_bp
    from .appointments.routes import appointments_bp
    from .records.routes import records_bp
    from .reports.routes import reports_bp
    from .main.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(main_bp)

    # 错误处理器
    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403

    with app.app_context():
        db.create_all()
        seed_data()
        ensure_metric_record_unique_constraint(app.logger)

    return app


def seed_data():
    dirty = False

    users = [
        ("admin", "admin"),
        ("staff", "staff"),
        ("user", "user"),
        ("user2", "user"),
    ]
    for username, role in users:
        if not User.query.filter_by(username=username).first():
            account = User(username=username, role=role)
            account.set_password("123456")
            db.session.add(account)
            dirty = True

    packages = [
        Package(name="基础体检套餐", description="基础指标筛查与常规检查", price=399),
        Package(name="全面体检套餐", description="全面指标检测与专项检查", price=899),
        Package(name="高端体检套餐", description="深度检测与个性化评估", price=1599),
    ]
    for package in packages:
        if not Package.query.filter_by(name=package.name).first():
            db.session.add(
                Package(
                    name=package.name,
                    description=package.description,
                    price=package.price,
                )
            )
            dirty = True

    metrics = [
        MetricDefinition(name="身高", unit="cm", normal_range="150-190", category="基本指标"),
        MetricDefinition(name="体重", unit="kg", normal_range="45-90", category="基本指标"),
        MetricDefinition(name="血压", unit="mmHg", normal_range="90-140", category="血液指标", suggestion="保持低盐饮食，适量运动"),
        MetricDefinition(name="血糖", unit="mmol/L", normal_range="3.9-6.1", category="血液指标", suggestion="控制糖分摄入，定期检测"),
        MetricDefinition(name="总胆固醇", unit="mmol/L", normal_range="3.0-5.2", category="血液指标", suggestion="减少高脂肪食物，增加运动"),
    ]
    for metric in metrics:
        if not MetricDefinition.query.filter_by(name=metric.name).first():
            db.session.add(
                MetricDefinition(
                    name=metric.name,
                    unit=metric.unit,
                    normal_range=metric.normal_range,
                    category=metric.category,
                    suggestion=metric.suggestion,
                )
            )
            dirty = True

    if not dirty:
        return

    try:
        db.session.commit()
    except IntegrityError:
        # Gunicorn multi-worker startup may race here; keep seed idempotent.
        db.session.rollback()
