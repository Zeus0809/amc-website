"""
Helper functions and decorators for authentication and authorization.
"""
from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    """
    Decorator to require admin privileges for a route.
    Must be used after @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # Unauthorized
        if not current_user.is_admin:
            abort(403)  # Forbidden - user is logged in but not admin
        return f(*args, **kwargs)
    return decorated_function


def approved_required(f):
    """
    Decorator to require approved status for a route.
    Must be used after @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # Unauthorized
        if not current_user.is_approved:
            # Redirect to pending approval page instead of 403
            from flask import redirect, url_for
            return redirect(url_for('auth.pending_approval'))
        return f(*args, **kwargs)
    return decorated_function
