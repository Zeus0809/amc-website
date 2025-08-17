from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - placeholder for now."""
    if request.method == 'POST':
        # TODO: Implement login logic in Chunk 2A
        flash('Login functionality coming in Chunk 2A!', 'info')
        return redirect(url_for('events.events_list'))
    
    return '<h1>AMC Login Page</h1><p>Login form coming in Chunk 2A!</p>'

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout - placeholder for now."""
    # TODO: Implement logout logic in Chunk 2A
    flash('Logout functionality coming in Chunk 2A!', 'info')
    return redirect(url_for('auth.login'))
