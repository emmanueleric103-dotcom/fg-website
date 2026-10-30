from flask import Blueprint, render_template
from flask_login import login_required

tools_bp = Blueprint('tools', __name__)

@tools_bp.route('/sensitivity')
def sensitivity():
    # Allow guest but show login prompt for save
    return render_template('tools/sensitivity.html')

@tools_bp.route('/cod')
def cod():
    return render_template('tools/sensitivity.html', default_tab='cod')
