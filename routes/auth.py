from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash
from models import db, User
from forms import LoginForm, RegistrationForm
from utils import admin_required

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with approval status checking."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        if current_user.is_approved:
            return redirect(url_for('events.events_list'))
        else:
            return redirect(url_for('auth.pending_approval'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Find user by username (case-insensitive)
        user = User.query.filter_by(username=form.username.data.lower()).first()
        
        # Check if user exists and password is correct
        if user and check_password_hash(user.password_hash, form.password.data):
            # Check if user account is active
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'error')
                return render_template('login.html', form=form)
            
            # Check if user is approved
            if not user.is_approved:
                # Log them in but redirect to pending approval page
                login_user(user)
                flash('Your account is pending administrator approval.', 'warning')
                return redirect(url_for('auth.pending_approval'))
            
            # All checks passed - log them in and redirect to events
            login_user(user)
            flash(f'Welcome back to AMC, {user.first_name}!', 'success')
            
            # Redirect to next page if provided, otherwise events page
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('events.events_list'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with admin approval workflow."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        if current_user.is_approved:
            return redirect(url_for('events.events_list'))
        else:
            return redirect(url_for('auth.pending_approval'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create new user (is_approved=False by default)
        user = User(
            username=form.username.data.lower(),
            email=form.email.data.lower(),
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        
        # Save to database
        try:
            db.session.add(user)
            db.session.commit()
            
            # Log them in immediately (but they'll be redirected to pending page)
            login_user(user)
            
            flash('Registration successful! Your account is pending administrator approval.', 'success')
            return redirect(url_for('auth.pending_approval'))
        
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html', form=form)


@auth_bp.route('/pending')
@login_required
def pending_approval():
    """Page for users whose accounts are pending approval."""
    # If user is already approved, redirect to events
    if current_user.is_approved:
        return redirect(url_for('events.events_list'))
    
    return render_template('pending_approval.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    username = current_user.first_name
    logout_user()
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


# Admin routes for user management
@auth_bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin interface to manage user accounts and approvals."""
    pending_users = User.get_pending_users()
    all_users = User.query.order_by(User.created_at.desc()).all()
    
    return render_template('admin/users.html', 
                         pending_users=pending_users, 
                         all_users=all_users)


@auth_bp.route('/admin/approve-user/<user_id>')
@login_required
@admin_required
def approve_user(user_id):
    """Approve a pending user account."""
    user = User.query.get_or_404(user_id)
    
    if not user.is_approved:
        user.is_approved = True
        db.session.commit()
        flash(f'User {user.username} has been approved!', 'success')
        
        # TODO: Send welcome email to user (console for MVP)
        print(f"CONSOLE EMAIL: Welcome {user.first_name}! Your AMC account has been approved.")
    else:
        flash(f'User {user.username} is already approved.', 'info')
    
    return redirect(url_for('auth.admin_users'))


@auth_bp.route('/admin/deny-user/<user_id>')
@login_required
@admin_required
def deny_user(user_id):
    """Deny/deactivate a user account."""
    user = User.query.get_or_404(user_id)
    
    # Deactivate the user instead of deleting
    user.deny()
    
    flash(f'User {user.username} has been denied/deactivated.', 'warning')
    
    # TODO: Send notification email to user (console for MVP)
    print(f"CONSOLE EMAIL: Sorry {user.first_name}, your AMC account application was not approved.")
    
    return redirect(url_for('auth.admin_users'))
