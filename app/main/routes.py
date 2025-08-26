from flask import render_template
from flask_login import login_required, current_user
from app.main import bp
from app.models import User

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    links_created = current_user.links.count()
    link_clicks = sum(link.clicks.count() for link in current_user.links)
    profile_views = 0  # Placeholder for now
    days_streak = 0    # Placeholder for now
    return render_template('index.html', title='Home',
                           links_created=links_created,
                           link_clicks=link_clicks,
                           profile_views=profile_views,
                           days_streak=days_streak)

from app.forms import LinkForm, EditProfileForm
from flask import flash, redirect, url_for, request
from app.models import Link, Click, Subscription, Plan
from app import db, csrf
from datetime import datetime, timedelta



@bp.route('/<username>')
def public_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    links = user.links.order_by(Link.timestamp.desc()).all()
    return render_template('public_profile.html', user=user, links=links)

@bp.route('/redirect/<int:link_id>')
def redirect_to_url(link_id):
    link = Link.query.get_or_404(link_id)
    click = Click(
        link_id=link.id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        referrer=request.referrer
    )
    db.session.add(click)
    db.session.commit()
    return redirect(link.url)

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = LinkForm()
    if form.validate_on_submit():
        if current_user.account_type == 'Free' and current_user.links.count() >= 2:
            flash('You have reached the maximum number of links for a free account. Please upgrade to add more.')
        else:
            link = Link(title=form.title.data, url=form.url.data, author=current_user)
            db.session.add(link)
            db.session.commit()
            flash('Your link has been added!')
        return redirect(url_for('main.dashboard'))
    links = current_user.links.order_by(Link.timestamp.desc()).all()
    total_clicks = sum(link.clicks.count() for link in links)

    show_form = True
    if current_user.account_type == 'Free' and len(links) >= 2:
        show_form = False

    return render_template('dashboard.html', user=current_user, links=links, form=form, total_clicks=total_clicks, show_form=show_form)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = secure_filename(form.picture.data.filename)
            picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_file)
            form.picture.data.save(picture_path)
            current_user.profile_picture = picture_file

        is_premium_theme = form.theme.data != 'default.css'
        can_use_premium = current_user.account_type != 'Free' or current_user.is_admin

        if is_premium_theme and not can_use_premium:
            flash('You must have a premium account to use this theme.')
        else:
            current_user.selected_theme = form.theme.data

        current_user.username = form.username.data
        current_user.bio = form.bio.data
        current_user.payment_link = form.payment_link.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.bio
        form.payment_link.data = current_user.payment_link
        form.theme.data = current_user.selected_theme
    return render_template('edit_profile.html', title='Edit Profile', form=form)

from paystackapi.customer import Customer
from paystackapi.transaction import Transaction
from paystackapi.subscription import Subscription as PaystackSubscription
from flask import current_app, abort, request
import hmac
import hashlib
import json
from werkzeug.utils import secure_filename
import os

@bp.route('/pricing')
@login_required
def pricing():
    plans = Plan.query.order_by(Plan.price).all()
    return render_template('pricing.html', title='Pricing', plans=plans)

@bp.route('/subscribe/<int:plan_id>')
@login_required
def subscribe(plan_id):
    plan = Plan.query.get_or_404(plan_id)

    if current_user.paystack_customer_code:
        customer_code = current_user.paystack_customer_code
    else:
        # Create a new customer on Paystack
        customer = Customer.create(
            email=current_user.email,
            first_name=current_user.username,
        )
        if customer['status']:
            customer_code = customer['data']['customer_code']
            current_user.paystack_customer_code = customer_code
            db.session.commit()
        else:
            flash('Could not create a customer account. Please try again.')
            return redirect(url_for('main.pricing'))

    # Create a subscription
    transaction = Transaction.initialize(
        email=current_user.email,
        amount=plan.price,
        plan=plan.paystack_plan_code,
        callback_url=url_for('main.dashboard', _external=True)
    )

    if transaction['status']:
        return redirect(transaction['data']['authorization_url'])
    else:
        flash('Could not start subscription. Please try again.')
        return redirect(url_for('main.pricing'))

@bp.route('/paystack-webhook', methods=['POST'])
@csrf.exempt
def paystack_webhook():
    # Verify the event by checking the signature
    signature = request.headers.get('x-paystack-signature')
    payload = request.get_data()
    secret_key = current_app.config['PAYSTACK_SECRET_KEY']

    hashed_payload = hmac.new(secret_key.encode('utf-8'), payload, hashlib.sha512).hexdigest()
    if signature != hashed_payload:
        abort(400)

    # Process the event
    event = json.loads(payload)
    if event['event'] == 'charge.success':
        customer_email = event['data']['customer']['email']
        plan_code = event['data'].get('plan', {}).get('plan_code')

        user = User.query.filter_by(email=customer_email).first()
        plan = Plan.query.filter_by(paystack_plan_code=plan_code).first()

        if user and plan:
            # Get subscription details from payload
            subscription_code = event['data'].get('subscription', {}).get('subscription_code')

            # Check for an existing active subscription to this plan
            subscription = Subscription.query.filter_by(user_id=user.id, plan_id=plan.id, status='active').first()

            if subscription and subscription.end_date > datetime.utcnow():
                # If user has an active subscription, extend it
                subscription.end_date = subscription.end_date + timedelta(days=30)
            else:
                # If subscription is expired or doesn't exist, create a new one
                if subscription: # In case it was expired
                    subscription.status = 'active'
                    subscription.start_date = datetime.utcnow()
                    subscription.end_date = datetime.utcnow() + timedelta(days=30)
                else:
                    subscription = Subscription(
                        user_id=user.id,
                        plan_id=plan.id,
                        paystack_subscription_code=subscription_code,
                        status='active',
                        start_date=datetime.utcnow(),
                        end_date=datetime.utcnow() + timedelta(days=30)
                    )
                    db.session.add(subscription)

            db.session.commit()

    return {'status': 'success'}, 200

@bp.route('/delete_link/<int:link_id>', methods=['POST'])
@login_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    if link.author != current_user:
        abort(403)
    db.session.delete(link)
    db.session.commit()
    flash('Your link has been deleted.')
    return redirect(url_for('main.dashboard'))

@bp.route('/cancel_subscription', methods=['POST'])
@login_required
def cancel_subscription():
    sub = current_user.subscriptions.filter_by(status='active').order_by(Subscription.end_date.desc()).first()
    if sub:
        # In a real app, you would call the Paystack API here to disable the subscription.
        # For example:
        # response = PaystackSubscription.disable(code=sub.paystack_subscription_code, token='<email_token_from_paystack>')
        # if response['status']:
        #     sub.status = 'cancelled'
        #     db.session.commit()
        #     flash('Your subscription has been cancelled and will not renew.')
        # else:
        #     flash('Could not cancel subscription with payment provider. Please contact support.')

        # For this project, we'll just update our local status.
        sub.status = 'cancelled'
        db.session.commit()
        flash('Your subscription has been cancelled. You will retain premium access until the end of your current billing period.')
    else:
        flash('No active subscription found to cancel.')

    return redirect(url_for('main.edit_profile'))