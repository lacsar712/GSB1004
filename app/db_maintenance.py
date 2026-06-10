from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from .extensions import db

UNIQUE_INDEX_NAME = "uq_metric_record_appointment_metric"


def _metric_record_unique_index_exists():
    inspector = inspect(db.engine)
    target_columns = {"appointment_id", "metric_definition_id"}

    for constraint in inspector.get_unique_constraints("metric_record"):
        columns = set(constraint.get("column_names") or [])
        if (
            constraint.get("name") == UNIQUE_INDEX_NAME
            or columns == target_columns
        ):
            return True

    for index in inspector.get_indexes("metric_record"):
        columns = set(index.get("column_names") or [])
        if (
            index.get("name") == UNIQUE_INDEX_NAME
            or (index.get("unique") and columns == target_columns)
        ):
            return True
    return False


def _count_duplicate_metric_records():
    duplicate_rows = db.session.execute(
        text(
            """
            SELECT COALESCE(SUM(cnt - 1), 0)
            FROM (
                SELECT COUNT(*) AS cnt
                FROM metric_record
                GROUP BY appointment_id, metric_definition_id
                HAVING COUNT(*) > 1
            ) t
            """
        )
    ).scalar()
    return int(duplicate_rows or 0)


def _delete_duplicate_metric_records_keep_latest():
    result = db.session.execute(
        text(
            """
            DELETE FROM metric_record
            WHERE id NOT IN (
                SELECT keep_id FROM (
                    SELECT
                        (
                            SELECT mr2.id
                            FROM metric_record mr2
                            WHERE mr2.appointment_id = mr1.appointment_id
                              AND mr2.metric_definition_id = mr1.metric_definition_id
                            ORDER BY mr2.recorded_at DESC, mr2.id DESC
                            LIMIT 1
                        ) AS keep_id
                    FROM metric_record mr1
                    GROUP BY mr1.appointment_id, mr1.metric_definition_id
                )
            )
            """
        )
    )
    return int(result.rowcount or 0)


def ensure_metric_record_unique_constraint(logger):
    if _metric_record_unique_index_exists():
        return

    duplicate_count = _count_duplicate_metric_records()
    deleted_count = 0

    if duplicate_count > 0:
        deleted_count = _delete_duplicate_metric_records_keep_latest()
        db.session.commit()

    try:
        db.session.execute(
            text(
                f"""
                CREATE UNIQUE INDEX IF NOT EXISTS {UNIQUE_INDEX_NAME}
                ON metric_record (appointment_id, metric_definition_id)
                """
            )
        )
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

    logger.info(
        "Metric record maintenance done: duplicates_before=%s, deleted=%s, index=%s",
        duplicate_count,
        deleted_count,
        UNIQUE_INDEX_NAME,
    )
