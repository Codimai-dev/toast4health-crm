"""Channel Partners routes."""

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db, require_module_access
from app.channel_partners import bp
from app.channel_partners.forms import ChannelPartnerForm
from app.models import ChannelPartner


@bp.route('/')
@login_required
@require_module_access('channel_partners')
def index():
    """Display all channel partners."""
    channel_partners = ChannelPartner.query.order_by(ChannelPartner.created_at.desc()).all()
    return render_template('channel_partners/index.html', title='Channel Partners', channel_partners=channel_partners)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@require_module_access('channel_partners')
def add():
    """Add a new channel partner."""
    form = ChannelPartnerForm()
    form.partner_code.data = ChannelPartner.generate_partner_code()
    if form.validate_on_submit():
        channel_partner = ChannelPartner(
            partner_code=form.partner_code.data,
            name=form.name.data,
            contact_no=form.contact_no.data,
            email=form.email.data,
            created_date=form.created_date.data,
            notes=form.notes.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(channel_partner)
        db.session.commit()
        flash('Channel partner added successfully!', 'success')
        return redirect(url_for('channel_partners.index'))
    return render_template('channel_partners/add.html', title='Add Channel Partner', form=form)


@bp.route('/view/<partner_code>')
@login_required
@require_module_access('channel_partners')
def view(partner_code):
    """View a channel partner."""
    partner = ChannelPartner.query.filter_by(partner_code=partner_code).first_or_404()
    return render_template('channel_partners/view.html', title='View Channel Partner', partner=partner)


@bp.route('/edit/<partner_code>', methods=['GET', 'POST'])
@login_required
@require_module_access('channel_partners')
def edit(partner_code):
    """Edit a channel partner."""
    partner = ChannelPartner.query.filter_by(partner_code=partner_code).first_or_404()
    form = ChannelPartnerForm(obj=partner)
    if form.validate_on_submit():
        form.populate_obj(partner)
        partner.updated_by = current_user.id
        db.session.commit()
        flash('Channel partner updated successfully!', 'success')
        return redirect(url_for('channel_partners.index'))
    return render_template('channel_partners/edit.html', title='Edit Channel Partner', form=form, partner=partner)