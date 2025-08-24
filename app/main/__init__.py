from flask import Blueprint
from flask_login import current_user
from app.models import Subscription
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.app_context_processor
def inject_subscription_status():
    if not current_user.is_authenticated or current_user.is_admin:
        return dict(in_grace_period=False, grace_period_end=None)

    # User is in grace period if they have no active subscription,
    # but their most recent subscription expired less than 7 days ago.
    if current_user.active_subscription:
        return dict(in_grace_period=False, grace_period_end=None)

    last_sub = current_user.subscriptions.order_by(Subscription.end_date.desc()).first()
    if not last_sub:
        return dict(in_grace_period=False, grace_period_end=None)

    if last_sub.end_date < datetime.utcnow():
        grace_period_end = last_sub.end_date + timedelta(days=7)
        if datetime.utcnow() < grace_period_end:
            return dict(in_grace_period=True, grace_period_end=grace_period_end)

    return dict(in_grace_period=False, grace_period_end=None)

from app.main import routes