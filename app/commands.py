import click
from flask.cli import with_appcontext
from app.models import User, Subscription
from app import db
from datetime import datetime, timedelta

# --- Users Command Group ---

@click.group(name='users')
def users():
    """User management commands."""
    pass

@users.command(name='grant-admin')
@with_appcontext
@click.argument('email')
def grant_admin(email):
    """Grants admin privileges to a user."""
    user = User.query.filter_by(email=email).first()
    if user is None:
        print(f"Error: User with email '{email}' not found.")
        return
    user.is_admin = True
    db.session.commit()
    print(f"User {user.username} (Email: {email}) has been granted admin privileges.")

# --- Subscriptions Command Group ---

@click.group(name='subscriptions')
def subscriptions():
    """Subscription management commands."""
    pass

from app.models import Plan

@click.group(name='plans')
def plans():
    """Plan management commands."""
    pass

@plans.command(name='seed')
@with_appcontext
def seed_plans():
    """Seeds the database with default subscription plans."""
    if Plan.query.count() > 0:
        print("Plans already exist. Aborting.")
        return

    free_plan = Plan(
        name='Free',
        price=0,
        features='Up to 5 Links\nBasic Analytics\nDefault Themes',
        paystack_plan_code='FREE_PLAN' # A placeholder for the free plan
    )

    premium_plan = Plan(
        name='Premium',
        price=100000, # 1000 NGN in kobo
        features='Unlimited Links\nAdvanced Analytics\nAll Premium Themes\nCustom Domains (Coming Soon)',
        paystack_plan_code='PLN_xxxxxxxxxxxxxxx' # Replace with your real Paystack Plan Code
    )

    db.session.add(free_plan)
    db.session.add(premium_plan)
    db.session.commit()
    print("Successfully seeded the database with default plans.")

@subscriptions.command(name='downgrade')
@with_appcontext
def downgrade_expired_subscriptions():
    """
    Finds all subscriptions that have expired past their grace period
    and downgrades the user to the 'free' account type.
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    expired_subscriptions = Subscription.query.filter(
        Subscription.status == 'active',
        Subscription.end_date < seven_days_ago
    ).all()

    if not expired_subscriptions:
        print("No expired subscriptions to downgrade.")
        return

    for sub in expired_subscriptions:
        user = sub.subscriber
        print(f"Downgrading user {user.username} (ID: {user.id}). Subscription {sub.id} has expired.")
        sub.status = 'expired'

    db.session.commit()
    print(f"Successfully downgraded {len(expired_subscriptions)} users.")

def init_app(app):
    app.cli.add_command(users)
    app.cli.add_command(subscriptions)
    app.cli.add_command(plans)