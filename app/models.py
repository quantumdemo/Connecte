from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta
from flask import current_app
import jwt

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False) # Price in kobo
    features = db.Column(db.Text, nullable=True)
    # paystack_plan_code is removed as we are no longer using Paystack's subscription plans

    def __repr__(self):
        return f'<Plan {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    links = db.relationship('Link', backref='author', lazy='dynamic', cascade="all, delete-orphan")
    bio = db.Column(db.String(140), nullable=True)
    payment_link = db.Column(db.String(200), nullable=True)
    selected_theme = db.Column(db.String(50), nullable=False, default='default.css')
    paystack_customer_code = db.Column(db.String(100), nullable=True)
    profile_picture = db.Column(db.String(100), nullable=False, default='default.jpg')
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    subscriptions = db.relationship('Subscription', backref='subscriber', lazy='dynamic', cascade="all, delete-orphan")

    # New fields for analytics
    profile_views = db.Column(db.Integer, default=0)
    last_login = db.Column(db.Date, nullable=True)
    login_streak = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': datetime.utcnow() + timedelta(seconds=expires_in)},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    @property
    def active_subscription(self):
        # A subscription is considered active for feature access if it's in 'active' or 'cancelled' state
        # and its end date has not yet passed.
        return self.subscriptions.filter(
            Subscription.status.in_(['active', 'cancelled']),
            Subscription.end_date > datetime.utcnow()
        ).order_by(Subscription.end_date.desc()).first()

    @property
    def account_type(self):
        if self.is_admin:
            return 'Admin'
        if self.active_subscription:
            return self.active_subscription.plan.name
        return 'Free'

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    # paystack_subscription_code is removed
    status = db.Column(db.String(20), nullable=False, default='inactive')
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    plan = db.relationship('Plan', backref=db.backref('subscriptions', lazy='dynamic'))

    def __repr__(self):
        return f'<Subscription {self.id}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Amount in kobo
    status = db.Column(db.String(20), nullable=False, default='pending')
    reference = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('payments', lazy='dynamic'))
    plan = db.relationship('Plan', backref=db.backref('payments', lazy='dynamic'))

    def __repr__(self):
        return f'<Payment {self.reference}>'

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    url = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    clicks = db.relationship('Click', backref='link', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return '<Link {}>'.format(self.title)

class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'))
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(200), nullable=True)
    referrer = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Click {self.timestamp}>'