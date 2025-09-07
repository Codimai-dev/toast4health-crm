"""Customers routes."""

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.customers import bp
from app.customers.forms import CustomerForm
from app.models import Customer


@bp.route('/')
@login_required
def index():
    """Display all customers."""
    customers = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template('customers/index.html', title='Customers', customers=customers)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new customer."""
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            customer_code=form.customer_code.data,
            customer_name=form.customer_name.data,
            contact_no=form.contact_no.data,
            email=form.email.data,
            services=form.services.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('customers.index'))
    return render_template('customers/add.html', title='Add Customer', form=form)


@bp.route('/view/<int:id>')
@login_required
def view(id):
    """View a customer."""
    customer = Customer.query.get_or_404(id)
    return render_template('customers/view.html', title='View Customer', customer=customer)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a customer."""
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        form.populate_obj(customer)
        customer.updated_by = current_user.id
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customers.index'))
    return render_template('customers/edit.html', title='Edit Customer', form=form, customer=customer)