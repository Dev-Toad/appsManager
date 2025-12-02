from datetime import datetime, timedelta
from sqlalchemy import func
from flask import render_template
from app.config import db
from app.models.user import User
from app.models.role import Role, Permission


def dashboard():

    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    one_hour_ago = now - timedelta(hours=1)

    stats = {
        "total_users": User.query.count(),
        "new_users_month": User.query.filter(User.created_at >= start_of_month).count(),
        "total_roles": Role.query.count(),
        "active_roles": Role.query.filter_by(active=True).count(),
        "active_users": User.query.filter_by(is_active=True).count(),
        "total_permissions": Permission.query.count(),
        "online_users": User.query.filter(User.last_login >= one_hour_ago).count(),
    }

    recent_activities = []
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    role_distribution_query = (
        db.session.query(Role.name, func.count(User.id))
        .join(User)
        .group_by(Role.name)
        .all()
    )

    role_distribution = dict(role_distribution_query)

    return render_template(
        "dashboard/dashboard.html",
        stats=stats,
        recent_activities=recent_activities,
        recent_users=recent_users,
        role_distribution=role_distribution,
    )
