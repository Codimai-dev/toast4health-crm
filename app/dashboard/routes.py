"""Dashboard routes with comprehensive CRM statistics."""

from datetime import datetime, date, timedelta
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, and_, or_

from app import db
from app.dashboard import bp
from app.models import (
    B2CLead, B2BLead, FollowUp, Customer, Booking, Employee,
    Expense, ChannelPartner, LeadStatus, LeadType
)


@bp.route('/')
@login_required
def index():
    """Dashboard with comprehensive CRM statistics."""

    try:
        # Date calculations
        today = date.today()

        # Get user's allowed modules
        allowed_modules = current_user.allowed_modules

        # Initialize stats as None - only populate if user has access
        b2c_stats = None
        b2b_stats = None
        follow_up_stats = None
        customer_stats = None
        booking_stats = None
        employee_stats = None
        expense_stats = None
        channel_partner_stats = None

        # Only populate statistics for modules user has access to
        if 'leads_b2c' in allowed_modules:
            b2c_stats = {
                'total': B2CLead.query.count(),
                'today': B2CLead.query.filter_by(enquiry_date=today).count(),
                'new': B2CLead.query.filter_by(status='NEW').count(),
                'follow_up': B2CLead.query.filter_by(status='FOLLOW_UP').count(),
                'prospect': B2CLead.query.filter_by(status='PROSPECT').count(),
                'converted': B2CLead.query.filter_by(status='CONVERTED').count(),
                'lost': B2CLead.query.filter_by(status='LOST').count(),
            }

        if 'leads_b2b' in allowed_modules:
            b2b_stats = {
                'total': B2BLead.query.count(),
                'today': B2BLead.query.filter_by(date=today).count(),
            }

        if 'follow_ups' in allowed_modules:
            follow_up_stats = {
                'due_today': FollowUp.query.filter_by(follow_up_on=today).count(),
                'due_tomorrow': FollowUp.query.filter_by(follow_up_on=today + timedelta(days=1)).count(),
                'overdue': FollowUp.query.filter(FollowUp.follow_up_on < today).count(),
                'total': FollowUp.query.count(),
            }

        if 'customers' in allowed_modules:
            customer_stats = {
                'total': Customer.query.count(),
                'with_bookings': db.session.query(func.count(func.distinct(Customer.id))).filter(Customer.bookings.any()).scalar() or 0,
            }

        if 'bookings' in allowed_modules:
            booking_stats = {
                'total': Booking.query.count(),
                'next_7_days': Booking.query.filter(Booking.start_date.between(today, today + timedelta(days=7))).count(),
                'pending_amount': db.session.query(func.sum(Booking.pending_amount)).scalar() or 0,
                'total_amount': db.session.query(func.sum(Booking.total_amount)).scalar() or 0,
                'paid_amount': db.session.query(func.sum(Booking.amount_paid)).scalar() or 0,
            }

        if 'employees' in allowed_modules:
            employee_stats = {
                'total': Employee.query.count(),
                'with_bookings': db.session.query(func.count(func.distinct(Employee.id))).filter(Employee.bookings.any()).scalar() or 0,
            }

        if 'expenses' in allowed_modules:
            expense_stats = {
                'total': Expense.query.count(),
                'last_30_days': Expense.query.filter(Expense.date >= today - timedelta(days=30)).count(),
                'amount_last_30_days': db.session.query(func.sum(Expense.expense_amount)).filter(Expense.date >= today - timedelta(days=30)).scalar() or 0,
                'total_amount': db.session.query(func.sum(Expense.expense_amount)).scalar() or 0,
            }

        if 'channel_partners' in allowed_modules:
            channel_partner_stats = {
                'total': ChannelPartner.query.count(),
                'with_customers': db.session.query(func.count(func.distinct(ChannelPartner.id))).filter(ChannelPartner.customers.any()).scalar() or 0,
            }

        return render_template('dashboard/index.html',
                              title='Dashboard',
                              b2c_stats=b2c_stats,
                              b2b_stats=b2b_stats,
                              follow_up_stats=follow_up_stats,
                              customer_stats=customer_stats,
                              booking_stats=booking_stats,
                              employee_stats=employee_stats,
                              expense_stats=expense_stats,
                              channel_partner_stats=channel_partner_stats,
                              today=today,
                              allowed_modules=allowed_modules)

    except Exception as e:
        # Fallback in case of any errors
        print(f"Dashboard error: {e}")
        return "Dashboard with statistics - System is initializing..."


@bp.route('/search')
@login_required
def search():
    """Global search across all CRM entities."""
    query = request.args.get('q', '').strip()

    if not query:
        return render_template('dashboard/search.html',
                              title='Search Results',
                              query=query,
                              results={})

    results = {}

    # Search B2C Leads
    b2c_results = B2CLead.query.filter(
        or_(
            B2CLead.customer_name.ilike(f'%{query}%'),
            B2CLead.contact_no.ilike(f'%{query}%'),
            B2CLead.email.ilike(f'%{query}%'),
            B2CLead.enquiry_id.ilike(f'%{query}%')
        )
    ).limit(10).all()
    if b2c_results:
        results['B2C Leads'] = b2c_results

    # Search B2B Leads
    b2b_results = B2BLead.query.filter(
        or_(
            B2BLead.organization_name.ilike(f'%{query}%'),
            B2BLead.organization_email.ilike(f'%{query}%'),
            B2BLead.t4h_spoc.ilike(f'%{query}%'),
            B2BLead.sr_no.ilike(f'%{query}%'),
            B2BLead.location.ilike(f'%{query}%'),
            B2BLead.org_poc_name_and_role.ilike(f'%{query}%')
        )
    ).limit(10).all()
    if b2b_results:
        results['B2B Leads'] = b2b_results

    # Search Customers
    customer_results = Customer.query.filter(
        or_(
            Customer.customer_name.ilike(f'%{query}%'),
            Customer.contact_no.ilike(f'%{query}%'),
            Customer.email.ilike(f'%{query}%'),
            Customer.customer_code.ilike(f'%{query}%')
        )
    ).limit(10).all()
    if customer_results:
        results['Customers'] = customer_results

    # Search Bookings
    booking_results = Booking.query.filter(
        or_(
            Booking.customer_name.ilike(f'%{query}%'),
            Booking.customer_mob.ilike(f'%{query}%'),
            Booking.booking_code.ilike(f'%{query}%'),
            Booking.services.ilike(f'%{query}%')
        )
    ).limit(10).all()
    if booking_results:
        results['Bookings'] = booking_results

    # Search Employees
    employee_results = Employee.query.filter(
        or_(
            Employee.name.ilike(f'%{query}%'),
            Employee.contact_no.ilike(f'%{query}%'),
            Employee.email.ilike(f'%{query}%'),
            Employee.employee_code.ilike(f'%{query}%'),
            Employee.designation.ilike(f'%{query}%')
        )
    ).limit(10).all()
    if employee_results:
        results['Employees'] = employee_results

    # Search Channel Partners
    partner_results = ChannelPartner.query.filter(
        or_(
            ChannelPartner.name.ilike(f'%{query}%'),
            ChannelPartner.contact_no.ilike(f'%{query}%'),
            ChannelPartner.email.ilike(f'%{query}%'),
            ChannelPartner.partner_code.ilike(f'%{query}%')
        )
    ).limit(10).all()
    if partner_results:
        results['Channel Partners'] = partner_results

    # Search Expenses
    expense_results = Expense.query.filter(
        or_(
            Expense.expense_code.ilike(f'%{query}%'),
            Expense.category.ilike(f'%{query}%'),
            Expense.sub_category.ilike(f'%{query}%')
        )
    ).limit(10).all()
    if expense_results:
        results['Expenses'] = expense_results

    return render_template('dashboard/search.html',
                          title='Search Results',
                          query=query,
                          results=results)


@bp.route('/api/chart-data')
@login_required
def chart_data():
    """API endpoint for dashboard chart data."""
    try:
        # Get date range from request (default to last 30 days)
        days = int(request.args.get('days', 30))
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        allowed_modules = current_user.allowed_modules
        chart_data = {}

        # Lead conversion funnel data
        if 'leads_b2c' in allowed_modules:
            funnel_data = {
                'labels': ['New', 'Follow Up', 'Prospect', 'Converted', 'Lost'],
                'datasets': [{
                    'label': 'B2C Leads',
                    'data': [
                        B2CLead.query.filter_by(status='new').count(),
                        B2CLead.query.filter_by(status='follow_up').count(),
                        B2CLead.query.filter_by(status='prospect').count(),
                        B2CLead.query.filter_by(status='converted').count(),
                        B2CLead.query.filter_by(status='lost').count(),
                    ],
                    'backgroundColor': [
                        'rgba(13, 110, 253, 0.8)',   # Blue
                        'rgba(255, 193, 7, 0.8)',    # Yellow
                        'rgba(13, 202, 240, 0.8)',   # Cyan
                        'rgba(25, 135, 84, 0.8)',    # Green
                        'rgba(108, 117, 125, 0.8)',  # Gray
                    ],
                    'borderColor': [
                        'rgba(13, 110, 253, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(13, 202, 240, 1)',
                        'rgba(25, 135, 84, 1)',
                        'rgba(108, 117, 125, 1)',
                    ],
                    'borderWidth': 1
                }]
            }
            chart_data['lead_funnel'] = funnel_data

        # Revenue trend data (last 30 days)
        if 'bookings' in allowed_modules:
            revenue_data = {
                'labels': [],
                'datasets': [{
                    'label': 'Revenue',
                    'data': [],
                    'borderColor': 'rgba(25, 135, 84, 1)',
                    'backgroundColor': 'rgba(25, 135, 84, 0.1)',
                    'fill': True,
                    'tension': 0.4
                }]
            }

            for i in range(days):
                current_date = start_date + timedelta(days=i)
                # Convert to datetime for proper comparison
                current_datetime = datetime.combine(current_date, datetime.min.time())
                next_datetime = datetime.combine(current_date + timedelta(days=1), datetime.min.time())

                daily_revenue = db.session.query(func.sum(Booking.total_amount)).filter(
                    Booking.created_at >= current_datetime,
                    Booking.created_at < next_datetime
                ).scalar() or 0

                revenue_data['labels'].append(current_date.strftime('%d/%m'))
                revenue_data['datasets'][0]['data'].append(float(daily_revenue))

            chart_data['revenue_trend'] = revenue_data

        # Performance metrics
        performance_data = {
            'labels': ['Leads', 'Customers', 'Bookings', 'Revenue'],
            'datasets': [{
                'label': 'Current Month',
                'data': [],
                'backgroundColor': 'rgba(13, 110, 253, 0.8)',
                'borderColor': 'rgba(13, 110, 253, 1)',
                'borderWidth': 1
            }]
        }

        # Calculate metrics for current month
        month_start = date.today().replace(day=1)

        if 'leads_b2c' in allowed_modules:
            monthly_leads = B2CLead.query.filter(B2CLead.created_at >= month_start).count()
        else:
            monthly_leads = 0

        if 'customers' in allowed_modules:
            monthly_customers = Customer.query.filter(Customer.created_at >= month_start).count()
        else:
            monthly_customers = 0

        if 'bookings' in allowed_modules:
            monthly_bookings = Booking.query.filter(Booking.created_at >= month_start).count()
            monthly_revenue = db.session.query(func.sum(Booking.total_amount)).filter(
                Booking.created_at >= month_start
            ).scalar() or 0
        else:
            monthly_bookings = 0
            monthly_revenue = 0

        performance_data['datasets'][0]['data'] = [
            monthly_leads,
            monthly_customers,
            monthly_bookings,
            float(monthly_revenue)
        ]

        chart_data['performance'] = performance_data

        return jsonify(chart_data)

    except Exception as e:
        print(f"Chart data error: {e}")
        return jsonify({'error': 'Failed to load chart data'}), 500