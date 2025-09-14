"""Expenses routes."""

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db, require_module_access
from app.expenses import bp
from app.expenses.forms import ExpenseForm
from app.models import Expense


@bp.route('/')
@login_required
@require_module_access('expenses')
def index():
    """Display all expenses."""
    expenses = Expense.query.order_by(Expense.created_at.desc()).all()
    return render_template('expenses/index.html', title='Expenses', expenses=expenses)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_module_access('expenses')
def add():
    """Add a new expense."""
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            expense_code=form.expense_code.data,
            date=form.date.data,
            category=form.category.data,
            sub_category=form.sub_category.data,
            expense_amount=form.expense_amount.data,
            booking_id=int(form.booking_id.data) if form.booking_id.data else None,
            other_id=form.other_id.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses.index'))
    return render_template('expenses/add.html', title='Add Expense', form=form)


@bp.route('/view/<int:id>')
@login_required
@require_module_access('expenses')
def view(id):
    """View an expense."""
    expense = Expense.query.get_or_404(id)
    return render_template('expenses/view.html', title='View Expense', expense=expense)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access('expenses')
def edit(id):
    """Edit an expense."""
    expense = Expense.query.get_or_404(id)
    form = ExpenseForm(obj=expense)
    if form.validate_on_submit():
        form.populate_obj(expense)
        expense.updated_by = current_user.id
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expenses.index'))
    return render_template('expenses/edit.html', title='Edit Expense', form=form, expense=expense)