"""Customers routes."""

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db, require_module_access
from app.customers import bp
from app.customers.forms import CustomerForm
from app.models import Customer


@bp.route('/')
@login_required
@require_module_access('customers')
def index():
    """Display all customers and converted B2C leads."""
    from app.models import B2CLead

    customers = Customer.query.order_by(Customer.created_at.desc()).all()
    converted_leads = B2CLead.query.filter_by(status='converted').order_by(B2CLead.created_at.desc()).all()

    # Combine customers and converted leads into a single list
    combined = []

    # Add customers
    for c in customers:
        combined.append({
            'id': c.id,
            'customer_code': c.customer_code,
            'customer_name': c.customer_name,
            'contact_no': c.contact_no,
            'email': c.email,
            'services': c.services,
            'is_converted_lead': False,
            'lead_id': None
        })

    # Add converted leads
    for l in converted_leads:
        combined.append({
            'id': l.enquiry_id,  # Use enquiry_id as id for leads
            'customer_code': l.enquiry_id,
            'customer_name': l.customer_name,
            'contact_no': l.contact_no,
            'email': l.email,
            'services': l.services,
            'is_converted_lead': True,
            'lead_id': l.enquiry_id
        })

    # Sort combined list by customer_code or some other field (assuming customer_code is sortable)
    combined.sort(key=lambda x: x['customer_code'], reverse=True)

    return render_template('customers/index.html', title='Customers', customers=combined)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_module_access('customers')
def add():
    """Add a new customer."""
    form = CustomerForm()
    form.customer_code.data = Customer.generate_customer_code()
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
@require_module_access('customers')
def view(id):
    """View a customer."""
    customer = Customer.query.get_or_404(id)
    return render_template('customers/view.html', title='View Customer', customer=customer)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access('customers')
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