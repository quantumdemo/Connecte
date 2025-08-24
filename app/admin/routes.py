from app.admin import bp
from flask import render_template, request, current_app, url_for, flash, redirect
from app.decorators import admin_required
from app.models import User, Subscription, Plan
from app import db
from flask_login import login_required, current_user
from datetime import datetime
from app.admin.forms import PlanForm

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    premium_users = db.session.query(User.id).join(User.subscriptions).filter(
        Subscription.status == 'active',
        Subscription.end_date > datetime.utcnow()
    ).distinct().count()

    # Simple revenue calculation: assume 1000 NGN per active subscription
    # In a real app, this would be more complex, likely summing actual transaction amounts.
    total_revenue = Subscription.query.filter_by(status='active').count() * 1000

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           premium_users=premium_users,
                           total_revenue=total_revenue)

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id.desc()).paginate(
        page, current_app.config.get('POSTS_PER_PAGE', 20), False)
    next_url = url_for('admin.users', page=users.next_num) if users.has_next else None
    prev_url = url_for('admin.users', page=users.prev_num) if users.has_prev else None
    return render_template('admin/users.html', users=users.items, next_url=next_url, prev_url=prev_url)

# Plan Management Routes
@bp.route('/plans')
@login_required
@admin_required
def plans():
    plans = Plan.query.order_by(Plan.price).all()
    return render_template('admin/plans.html', plans=plans)

@bp.route('/plans/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_plan():
    form = PlanForm()
    if form.validate_on_submit():
        plan = Plan(name=form.name.data,
                    price=form.price.data,
                    features=form.features.data,
                    paystack_plan_code=form.paystack_plan_code.data)
        db.session.add(plan)
        db.session.commit()
        flash('New plan has been created.', 'success')
        return redirect(url_for('admin.plans'))
    return render_template('admin/plan_form.html', form=form, title='Create New Plan')

@bp.route('/plans/edit/<int:plan_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    form = PlanForm(obj=plan)
    if form.validate_on_submit():
        plan.name = form.name.data
        plan.price = form.price.data
        plan.features = form.features.data
        plan.paystack_plan_code = form.paystack_plan_code.data
        db.session.commit()
        flash('The plan has been updated.', 'success')
        return redirect(url_for('admin.plans'))
    return render_template('admin/plan_form.html', form=form, title='Edit Plan')

@bp.route('/plans/delete/<int:plan_id>', methods=['POST'])
@login_required
@admin_required
def delete_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    if plan.subscriptions.count() > 0:
        flash('Cannot delete a plan that has active subscriptions.', 'danger')
        return redirect(url_for('admin.plans'))
    db.session.delete(plan)
    db.session.commit()
    flash('The plan has been deleted.', 'success')
    return redirect(url_for('admin.plans'))

@bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin.users'))