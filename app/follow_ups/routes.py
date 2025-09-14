"""Follow-ups routes."""

from flask import render_template
from flask_login import login_required

from app import require_module_access
from app.follow_ups import bp
from app.models import FollowUp


@bp.route('/')
@login_required
@require_module_access('follow_ups')
def index():
    """Display all follow-ups categorized by B2C and B2B."""

    # Get all follow-ups ordered by date
    all_follow_ups = FollowUp.query.order_by(FollowUp.follow_up_on.desc()).all()

    # Separate into B2C and B2B
    b2c_follow_ups = [fu for fu in all_follow_ups if fu.lead_type.value == 'B2C']
    b2b_follow_ups = [fu for fu in all_follow_ups if fu.lead_type.value == 'B2B']

    return render_template('follow_ups/index.html', title='Follow-ups',
                         b2c_follow_ups=b2c_follow_ups, b2b_follow_ups=b2b_follow_ups)