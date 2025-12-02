from flask import jsonify
from app.config import db
from app.models.application import Framework


def frameworks_by_stack(stack_id):
    frameworks = db.session.execute(
        db.select(Framework)
        .where(Framework.stack_id == stack_id)
        .order_by(Framework.name)
    ).scalars()

    return jsonify([{"id": fw.id, "name": fw.name} for fw in frameworks])
