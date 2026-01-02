"""Finance routes."""

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from datetime import datetime, date

from app import db, require_module_access
from app.finance import bp
from app.finance.forms import (SaleForm, PurchaseForm, PaymentReceivedForm, 
                               PaymentMadeForm, ChartOfAccountForm)
from app.models import Sale, Purchase, PaymentReceived, PaymentMade, ChartOfAccount, Customer


# ==================== DASHBOARD ====================
@bp.route('/dashboard')
@login_required
@require_module_access('finance')
def dashboard():
    """Display financial dashboard with summary."""
    # Get current year and month
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Calculate totals for current year
    # Total Revenue = Sales invoices + Standalone payments received (not linked to sales)
    total_sales = db.session.query(func.sum(Sale.amount)).filter(
        extract('year', Sale.date) == current_year
    ).scalar() or 0
    
    # Add standalone payments (payments not linked to any sale invoice)
    standalone_payments = db.session.query(func.sum(PaymentReceived.amount)).filter(
        extract('year', PaymentReceived.date) == current_year,
        PaymentReceived.sale_id.is_(None)
    ).scalar() or 0
    
    total_revenue = total_sales + standalone_payments
    
    total_purchases = db.session.query(func.sum(Purchase.amount)).filter(
        extract('year', Purchase.date) == current_year
    ).scalar() or 0
    
    from app.models import Expense
    total_expenses = db.session.query(func.sum(Expense.expense_amount)).filter(
        extract('year', Expense.date) == current_year
    ).scalar() or 0
    
    total_payments_received = db.session.query(func.sum(PaymentReceived.amount)).filter(
        extract('year', PaymentReceived.date) == current_year
    ).scalar() or 0
    
    total_payments_made = db.session.query(func.sum(PaymentMade.amount)).filter(
        extract('year', PaymentMade.date) == current_year
    ).scalar() or 0
    
    # Calculate derived metrics
    gross_profit = total_revenue - total_purchases
    net_profit = gross_profit - total_expenses
    cash_position = total_payments_received - total_payments_made
    
    # Transaction counts
    # For revenue count: sales invoices + standalone payments
    sales_count = Sale.query.filter(extract('year', Sale.date) == current_year).count()
    standalone_payments_count = PaymentReceived.query.filter(
        extract('year', PaymentReceived.date) == current_year,
        PaymentReceived.sale_id.is_(None)
    ).count()
    revenue_count = sales_count + standalone_payments_count
    
    purchases_count = Purchase.query.filter(extract('year', Purchase.date) == current_year).count()
    expenses_count = Expense.query.filter(extract('year', Expense.date) == current_year).count()
    payments_received_count = PaymentReceived.query.filter(extract('year', PaymentReceived.date) == current_year).count()
    payments_made_count = PaymentMade.query.filter(extract('year', PaymentMade.date) == current_year).count()
    
    # Recent transactions
    recent_sales = Sale.query.order_by(Sale.date.desc()).limit(5).all()
    recent_purchases = Purchase.query.order_by(Purchase.date.desc()).limit(5).all()
    recent_payments_received = PaymentReceived.query.order_by(PaymentReceived.date.desc()).limit(5).all()
    recent_payments_made = PaymentMade.query.order_by(PaymentMade.date.desc()).limit(5).all()
    
    # Monthly summary for current year
    monthly_data = []
    for month in range(1, 13):
        month_sales = db.session.query(func.sum(Sale.amount)).filter(
            extract('year', Sale.date) == current_year,
            extract('month', Sale.date) == month
        ).scalar() or 0
        
        # Add standalone payments for the month
        month_standalone_payments = db.session.query(func.sum(PaymentReceived.amount)).filter(
            extract('year', PaymentReceived.date) == current_year,
            extract('month', PaymentReceived.date) == month,
            PaymentReceived.sale_id.is_(None)
        ).scalar() or 0
        
        month_revenue = month_sales + month_standalone_payments
        
        month_purchases = db.session.query(func.sum(Purchase.amount)).filter(
            extract('year', Purchase.date) == current_year,
            extract('month', Purchase.date) == month
        ).scalar() or 0
        
        month_expenses = db.session.query(func.sum(Expense.expense_amount)).filter(
            extract('year', Expense.date) == current_year,
            extract('month', Expense.date) == month
        ).scalar() or 0
        
        month_payments_received = db.session.query(func.sum(PaymentReceived.amount)).filter(
            extract('year', PaymentReceived.date) == current_year,
            extract('month', PaymentReceived.date) == month
        ).scalar() or 0
        
        month_payments_made = db.session.query(func.sum(PaymentMade.amount)).filter(
            extract('year', PaymentMade.date) == current_year,
            extract('month', PaymentMade.date) == month
        ).scalar() or 0
        
        month_net_profit = month_revenue - month_purchases - month_expenses
        
        monthly_data.append({
            'month': month,
            'month_name': date(current_year, month, 1).strftime('%B'),
            'sales': float(month_revenue),  # Changed to show total revenue in chart
            'purchases': float(month_purchases),
            'expenses': float(month_expenses),
            'payments_received': float(month_payments_received),
            'payments_made': float(month_payments_made),
            'net_profit': float(month_net_profit)
        })
    
    return render_template('finance/dashboard.html',
                         title='Financial Dashboard',
                         total_revenue=total_revenue,
                         total_purchases=total_purchases,
                         total_expenses=total_expenses,
                         total_payments_received=total_payments_received,
                         total_payments_made=total_payments_made,
                         gross_profit=gross_profit,
                         net_profit=net_profit,
                         cash_position=cash_position,
                         revenue_count=revenue_count,
                         purchases_count=purchases_count,
                         expenses_count=expenses_count,
                         payments_received_count=payments_received_count,
                         payments_made_count=payments_made_count,
                         recent_sales=recent_sales,
                         recent_purchases=recent_purchases,
                         recent_payments_received=recent_payments_received,
                         recent_payments_made=recent_payments_made,
                         monthly_data=monthly_data,
                         current_year=current_year)


# ==================== SALES ====================
@bp.route('/sales')
@login_required
@require_module_access('finance')
def sales():
    """Display all sales."""
    sales = Sale.query.order_by(Sale.date.desc()).all()
    return render_template('finance/sales/index.html', title='Sales', sales=sales)


@bp.route('/sales/add', methods=['GET', 'POST'])
@login_required
@require_module_access('finance')
def sales_add():
    """Add a new sale."""
    form = SaleForm()
    if form.validate_on_submit():
        # Use new customer name if provided, otherwise use selected
        customer_name = form.customer_name_new.data.strip() if form.customer_name_new.data else form.customer_name.data
        
        # Find customer_id if customer exists
        customer = Customer.query.filter_by(customer_name=customer_name).first()
        customer_id = customer.id if customer else None
        
        sale = Sale(
            invoice_number=Sale.generate_invoice_number(),
            date=form.date.data,
            customer_name=customer_name,
            customer_id=customer_id,
            product_service=form.product_service.data,
            amount=form.amount.data,
            payment_status=form.payment_status.data,
            notes=form.notes.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(sale)
        db.session.flush()  # Flush to get the sale.id
        
        # If payment status is Received or Partial, create a PaymentReceived entry
        if form.payment_status.data in ['Received', 'Partial']:
            # Validate payment fields
            if not form.payment_amount.data or form.payment_amount.data <= 0:
                flash('Payment amount is required when payment status is Received or Partial!', 'danger')
                db.session.rollback()
                return render_template('finance/sales/add.html', title='Add Sale', form=form)
            
            if not form.payment_date.data:
                flash('Payment date is required when payment status is Received or Partial!', 'danger')
                db.session.rollback()
                return render_template('finance/sales/add.html', title='Add Sale', form=form)
            
            if not form.payment_method.data:
                flash('Payment method is required when payment status is Received or Partial!', 'danger')
                db.session.rollback()
                return render_template('finance/sales/add.html', title='Add Sale', form=form)
            
            payment = PaymentReceived(
                reference_number=PaymentReceived.generate_reference_number(),
                date=form.payment_date.data,
                customer_name=customer_name,
                customer_id=customer_id,
                amount=form.payment_amount.data,
                payment_method=form.payment_method.data,
                invoice_number=sale.invoice_number,
                sale_id=sale.id,
                remarks=form.payment_remarks.data or f"Payment for {sale.invoice_number}",
                created_by=current_user.id,
                updated_by=current_user.id
            )
            db.session.add(payment)
        
        db.session.commit()
        flash('Sale added successfully!', 'success')
        if form.payment_status.data in ['Received', 'Partial']:
            flash('Payment received entry created automatically!', 'info')
        return redirect(url_for('finance.sales'))
    
    # Pre-populate invoice number
    form.invoice_number.data = Sale.generate_invoice_number()
    form.date.data = date.today()
    form.payment_date.data = date.today()
    return render_template('finance/sales/add.html', title='Add Sale', form=form)


@bp.route('/sales/view/<int:id>')
@login_required
@require_module_access('finance')
def sales_view(id):
    """View a sale."""
    sale = Sale.query.get_or_404(id)
    return render_template('finance/sales/view.html', title='View Sale', sale=sale)


@bp.route('/sales/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access('finance')
def sales_edit(id):
    """Edit a sale."""
    sale = Sale.query.get_or_404(id)
    form = SaleForm(obj=sale)
    
    if form.validate_on_submit():
        # Use new customer name if provided, otherwise use selected
        customer_name = form.customer_name_new.data.strip() if form.customer_name_new.data else form.customer_name.data
        
        # Find customer_id if customer exists
        customer = Customer.query.filter_by(customer_name=customer_name).first()
        
        # Store old payment status to detect changes
        old_payment_status = sale.payment_status
        
        sale.date = form.date.data
        sale.customer_name = customer_name
        sale.customer_id = customer.id if customer else None
        sale.product_service = form.product_service.data
        sale.amount = form.amount.data
        sale.payment_status = form.payment_status.data
        sale.notes = form.notes.data
        sale.updated_by = current_user.id
        
        # Handle payment received entry
        if form.payment_status.data in ['Received', 'Partial']:
            # Validate payment fields
            if not form.payment_amount.data or form.payment_amount.data <= 0:
                flash('Payment amount is required when payment status is Received or Partial!', 'danger')
                db.session.rollback()
                return render_template('finance/sales/edit.html', title='Edit Sale', form=form, sale=sale)
            
            if not form.payment_date.data:
                flash('Payment date is required when payment status is Received or Partial!', 'danger')
                db.session.rollback()
                return render_template('finance/sales/edit.html', title='Edit Sale', form=form, sale=sale)
            
            if not form.payment_method.data:
                flash('Payment method is required when payment status is Received or Partial!', 'danger')
                db.session.rollback()
                return render_template('finance/sales/edit.html', title='Edit Sale', form=form, sale=sale)
            
            # Check if there's already a payment for this sale
            existing_payment = PaymentReceived.query.filter_by(sale_id=sale.id).first()
            
            if existing_payment:
                # Update existing payment
                existing_payment.date = form.payment_date.data
                existing_payment.customer_name = customer_name
                existing_payment.customer_id = customer.id if customer else None
                existing_payment.amount = form.payment_amount.data
                existing_payment.payment_method = form.payment_method.data
                existing_payment.remarks = form.payment_remarks.data or f"Payment for {sale.invoice_number}"
                existing_payment.updated_by = current_user.id
                flash('Sale and payment received entry updated successfully!', 'success')
            else:
                # Create new payment entry
                payment = PaymentReceived(
                    reference_number=PaymentReceived.generate_reference_number(),
                    date=form.payment_date.data,
                    customer_name=customer_name,
                    customer_id=customer.id if customer else None,
                    amount=form.payment_amount.data,
                    payment_method=form.payment_method.data,
                    invoice_number=sale.invoice_number,
                    sale_id=sale.id,
                    remarks=form.payment_remarks.data or f"Payment for {sale.invoice_number}",
                    created_by=current_user.id,
                    updated_by=current_user.id
                )
                db.session.add(payment)
                flash('Sale updated and payment received entry created successfully!', 'success')
        elif old_payment_status in ['Received', 'Partial'] and form.payment_status.data == 'Pending':
            # Payment status changed from Received/Partial to Pending
            # Optionally delete the payment entry (or just update the sale)
            flash('Sale updated successfully! Note: Existing payment entry was not deleted.', 'warning')
        else:
            flash('Sale updated successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('finance.sales'))
    
    # Pre-populate form
    if not form.is_submitted():
        form.customer_name.data = sale.customer_name
        
        # Pre-populate payment fields if there's an existing payment
        existing_payment = PaymentReceived.query.filter_by(sale_id=sale.id).first()
        if existing_payment:
            form.payment_amount.data = existing_payment.amount
            form.payment_date.data = existing_payment.date
            form.payment_method.data = existing_payment.payment_method
            form.payment_remarks.data = existing_payment.remarks
    
    return render_template('finance/sales/edit.html', title='Edit Sale', form=form, sale=sale)


@bp.route('/sales/delete/<int:id>')
@login_required
@require_module_access('finance')
def sales_delete(id):
    """Delete a sale."""
    sale = Sale.query.get_or_404(id)
    db.session.delete(sale)
    db.session.commit()
    flash('Sale deleted successfully!', 'success')
    return redirect(url_for('finance.sales'))


# ==================== PURCHASES ====================
@bp.route('/purchases')
@login_required
@require_module_access('finance')
def purchases():
    """Display all purchases."""
    purchases = Purchase.query.order_by(Purchase.date.desc()).all()
    return render_template('finance/purchases/index.html', title='Purchases', purchases=purchases)


@bp.route('/purchases/add', methods=['GET', 'POST'])
@login_required
@require_module_access('finance')
def purchases_add():
    """Add a new purchase."""
    form = PurchaseForm()
    if form.validate_on_submit():
        purchase = Purchase(
            bill_number=Purchase.generate_bill_number(),
            date=form.date.data,
            vendor_name=form.vendor_name.data,
            item_description=form.item_description.data,
            amount=form.amount.data,
            payment_status=form.payment_status.data,
            notes=form.notes.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(purchase)
        db.session.commit()
        flash('Purchase added successfully!', 'success')
        return redirect(url_for('finance.purchases'))
    
    # Pre-populate bill number
    form.bill_number.data = Purchase.generate_bill_number()
    form.date.data = date.today()
    return render_template('finance/purchases/add.html', title='Add Purchase', form=form)


@bp.route('/purchases/view/<int:id>')
@login_required
@require_module_access('finance')
def purchases_view(id):
    """View a purchase."""
    purchase = Purchase.query.get_or_404(id)
    return render_template('finance/purchases/view.html', title='View Purchase', purchase=purchase)


@bp.route('/purchases/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access('finance')
def purchases_edit(id):
    """Edit a purchase."""
    purchase = Purchase.query.get_or_404(id)
    form = PurchaseForm(obj=purchase)
    
    if form.validate_on_submit():
        purchase.date = form.date.data
        purchase.vendor_name = form.vendor_name.data
        purchase.item_description = form.item_description.data
        purchase.amount = form.amount.data
        purchase.payment_status = form.payment_status.data
        purchase.notes = form.notes.data
        purchase.updated_by = current_user.id
        
        db.session.commit()
        flash('Purchase updated successfully!', 'success')
        return redirect(url_for('finance.purchases'))
    
    return render_template('finance/purchases/edit.html', title='Edit Purchase', form=form, purchase=purchase)


@bp.route('/purchases/delete/<int:id>')
@login_required
@require_module_access('finance')
def purchases_delete(id):
    """Delete a purchase."""
    purchase = Purchase.query.get_or_404(id)
    db.session.delete(purchase)
    db.session.commit()
    flash('Purchase deleted successfully!', 'success')
    return redirect(url_for('finance.purchases'))


# ==================== PAYMENTS RECEIVED ====================
@bp.route('/payments-received')
@login_required
@require_module_access('finance')
def payments_received():
    """Display all payments received."""
    payments = PaymentReceived.query.order_by(PaymentReceived.date.desc()).all()
    return render_template('finance/payments_received/index.html', title='Payments Received', payments=payments)


@bp.route('/payments-received/add', methods=['GET', 'POST'])
@login_required
@require_module_access('finance')
def payments_received_add():
    """Add a new payment received."""
    form = PaymentReceivedForm()
    if form.validate_on_submit():
        # Use new customer name if provided, otherwise use selected
        customer_name = form.customer_name_new.data.strip() if form.customer_name_new.data else form.customer_name.data
        
        # Find customer_id if customer exists
        customer = Customer.query.filter_by(customer_name=customer_name).first()
        customer_id = customer.id if customer else None
        
        # Find sale_id if invoice is selected
        sale_id = None
        if form.invoice_number.data:
            sale = Sale.query.filter_by(invoice_number=form.invoice_number.data).first()
            sale_id = sale.id if sale else None
        
        payment = PaymentReceived(
            reference_number=PaymentReceived.generate_reference_number(),
            date=form.date.data,
            customer_name=customer_name,
            customer_id=customer_id,
            amount=form.amount.data,
            payment_method=form.payment_method.data,
            invoice_number=form.invoice_number.data if form.invoice_number.data else None,
            sale_id=sale_id,
            remarks=form.remarks.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(payment)
        db.session.commit()
        flash('Payment received added successfully!', 'success')
        return redirect(url_for('finance.payments_received'))
    
    # Pre-populate reference number
    form.reference_number.data = PaymentReceived.generate_reference_number()
    form.date.data = date.today()
    return render_template('finance/payments_received/add.html', title='Add Payment Received', form=form)


@bp.route('/payments-received/view/<int:id>')
@login_required
@require_module_access('finance')
def payments_received_view(id):
    """View a payment received."""
    payment = PaymentReceived.query.get_or_404(id)
    return render_template('finance/payments_received/view.html', title='View Payment Received', payment=payment)


@bp.route('/payments-received/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access('finance')
def payments_received_edit(id):
    """Edit a payment received."""
    payment = PaymentReceived.query.get_or_404(id)
    form = PaymentReceivedForm(obj=payment)
    
    if form.validate_on_submit():
        # Use new customer name if provided, otherwise use selected
        customer_name = form.customer_name_new.data.strip() if form.customer_name_new.data else form.customer_name.data
        
        # Find customer_id if customer exists
        customer = Customer.query.filter_by(customer_name=customer_name).first()
        
        # Find sale_id if invoice is selected
        sale_id = None
        if form.invoice_number.data:
            sale = Sale.query.filter_by(invoice_number=form.invoice_number.data).first()
            sale_id = sale.id if sale else None
        
        payment.date = form.date.data
        payment.customer_name = customer_name
        payment.customer_id = customer.id if customer else None
        payment.amount = form.amount.data
        payment.payment_method = form.payment_method.data
        payment.invoice_number = form.invoice_number.data if form.invoice_number.data else None
        payment.sale_id = sale_id
        payment.remarks = form.remarks.data
        payment.updated_by = current_user.id
        
        db.session.commit()
        flash('Payment received updated successfully!', 'success')
        return redirect(url_for('finance.payments_received'))
    
    # Pre-populate form
    if not form.is_submitted():
        form.customer_name.data = payment.customer_name
        form.invoice_number.data = payment.invoice_number
    
    return render_template('finance/payments_received/edit.html', title='Edit Payment Received', form=form, payment=payment)


@bp.route('/payments-received/delete/<int:id>')
@login_required
@require_module_access('finance')
def payments_received_delete(id):
    """Delete a payment received."""
    payment = PaymentReceived.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    flash('Payment received deleted successfully!', 'success')
    return redirect(url_for('finance.payments_received'))


# ==================== PAYMENTS MADE ====================
@bp.route('/payments-made')
@login_required
@require_module_access('finance')
def payments_made():
    """Display all payments made."""
    payments = PaymentMade.query.order_by(PaymentMade.date.desc()).all()
    return render_template('finance/payments_made/index.html', title='Payments Made', payments=payments)


@bp.route('/payments-made/add', methods=['GET', 'POST'])
@login_required
@require_module_access('finance')
def payments_made_add():
    """Add a new payment made."""
    form = PaymentMadeForm()
    if form.validate_on_submit():
        # Find purchase_id if bill is selected
        purchase_id = None
        if form.bill_number.data:
            purchase = Purchase.query.filter_by(bill_number=form.bill_number.data).first()
            purchase_id = purchase.id if purchase else None
        
        payment = PaymentMade(
            reference_number=PaymentMade.generate_reference_number(),
            date=form.date.data,
            payee_name=form.payee_name.data,
            amount=form.amount.data,
            payment_method=form.payment_method.data,
            bill_number=form.bill_number.data if form.bill_number.data else None,
            purchase_id=purchase_id,
            category=form.category.data,
            remarks=form.remarks.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(payment)
        db.session.commit()
        flash('Payment made added successfully!', 'success')
        return redirect(url_for('finance.payments_made'))
    
    # Pre-populate reference number
    form.reference_number.data = PaymentMade.generate_reference_number()
    form.date.data = date.today()
    return render_template('finance/payments_made/add.html', title='Add Payment Made', form=form)


@bp.route('/payments-made/view/<int:id>')
@login_required
@require_module_access('finance')
def payments_made_view(id):
    """View a payment made."""
    payment = PaymentMade.query.get_or_404(id)
    return render_template('finance/payments_made/view.html', title='View Payment Made', payment=payment)


@bp.route('/payments-made/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access('finance')
def payments_made_edit(id):
    """Edit a payment made."""
    payment = PaymentMade.query.get_or_404(id)
    form = PaymentMadeForm(obj=payment)
    
    if form.validate_on_submit():
        # Find purchase_id if bill is selected
        purchase_id = None
        if form.bill_number.data:
            purchase = Purchase.query.filter_by(bill_number=form.bill_number.data).first()
            purchase_id = purchase.id if purchase else None
        
        payment.date = form.date.data
        payment.payee_name = form.payee_name.data
        payment.amount = form.amount.data
        payment.payment_method = form.payment_method.data
        payment.bill_number = form.bill_number.data if form.bill_number.data else None
        payment.purchase_id = purchase_id
        payment.category = form.category.data
        payment.remarks = form.remarks.data
        payment.updated_by = current_user.id
        
        db.session.commit()
        flash('Payment made updated successfully!', 'success')
        return redirect(url_for('finance.payments_made'))
    
    # Pre-populate form
    if not form.is_submitted():
        form.bill_number.data = payment.bill_number
    
    return render_template('finance/payments_made/edit.html', title='Edit Payment Made', form=form, payment=payment)


@bp.route('/payments-made/delete/<int:id>')
@login_required
@require_module_access('finance')
def payments_made_delete(id):
    """Delete a payment made."""
    payment = PaymentMade.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    flash('Payment made deleted successfully!', 'success')
    return redirect(url_for('finance.payments_made'))


# ==================== CHART OF ACCOUNTS ====================
@bp.route('/chart-of-accounts')
@login_required
@require_module_access('finance')
def chart_of_accounts():
    """Display chart of accounts."""
    accounts = ChartOfAccount.query.order_by(ChartOfAccount.account_code).all()
    return render_template('finance/chart_of_accounts/index.html', title='Chart of Accounts', accounts=accounts)


@bp.route('/chart-of-accounts/add', methods=['GET', 'POST'])
@login_required
@require_module_access('finance')
def chart_of_accounts_add():
    """Add a new account."""
    form = ChartOfAccountForm()
    if form.validate_on_submit():
        account = ChartOfAccount(
            account_code=form.account_code.data,
            account_name=form.account_name.data,
            account_type=form.account_type.data,
            description=form.description.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(account)
        db.session.commit()
        flash('Account added successfully!', 'success')
        return redirect(url_for('finance.chart_of_accounts'))
    
    return render_template('finance/chart_of_accounts/add.html', title='Add Account', form=form)


@bp.route('/chart-of-accounts/view/<int:id>')
@login_required
@require_module_access('finance')
def chart_of_accounts_view(id):
    """View an account."""
    account = ChartOfAccount.query.get_or_404(id)
    return render_template('finance/chart_of_accounts/view.html', title='View Account', account=account)


@bp.route('/chart-of-accounts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access('finance')
def chart_of_accounts_edit(id):
    """Edit an account."""
    account = ChartOfAccount.query.get_or_404(id)
    form = ChartOfAccountForm(obj=account)
    
    if form.validate_on_submit():
        account.account_code = form.account_code.data
        account.account_name = form.account_name.data
        account.account_type = form.account_type.data
        account.description = form.description.data
        account.updated_by = current_user.id
        
        db.session.commit()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('finance.chart_of_accounts'))
    
    return render_template('finance/chart_of_accounts/edit.html', title='Edit Account', form=form, account=account)


@bp.route('/chart-of-accounts/delete/<int:id>')
@login_required
@require_module_access('finance')
def chart_of_accounts_delete(id):
    """Delete an account."""
    account = ChartOfAccount.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    flash('Account deleted successfully!', 'success')
    return redirect(url_for('finance.chart_of_accounts'))
