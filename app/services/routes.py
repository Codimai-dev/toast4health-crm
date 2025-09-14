"""Services routes."""

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db, require_module_access
from app.services import bp
from app.services.forms import ServiceForm
from app.models import Service


@bp.route('/')
@login_required
@require_module_access('services')
def index():
    """Display all services."""
    services = Service.query.order_by(Service.created_at.desc()).all()
    return render_template('services/index.html', title='Services', services=services)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_module_access('services')
def add():
    """Add a new service."""
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            description=form.description.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(service)
        db.session.commit()
        flash('Service added successfully!', 'success')
        return redirect(url_for('services.index'))
    return render_template('services/add.html', title='Add Service', form=form)


@bp.route('/view/<int:id>')
@login_required
@require_module_access('services')
def view(id):
    """View a service."""
    service = Service.query.get_or_404(id)
    return render_template('services/view.html', title='View Service', service=service)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access('services')
def edit(id):
    """Edit a service."""
    service = Service.query.get_or_404(id)
    form = ServiceForm(obj=service)
    if form.validate_on_submit():
        form.populate_obj(service)
        service.updated_by = current_user.id
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('services.index'))
    return render_template('services/edit.html', title='Edit Service', form=form, service=service)