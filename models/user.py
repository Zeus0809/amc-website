"""
User model for AMC Website
    # Relationships - Users connect to Events through RSVP join table
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .database import db, generate_uuid

class User(UserMixin, db.Model):
    """
    User model with authentication and approval workflow
    """
    __tablename__ = 'users'
    
    # Primary key - UUID for security
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    
    # Authentication fields
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Personal information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Status fields for approval workflow
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)  # Admin approval required
    is_admin = db.Column(db.Boolean, default=False, nullable=False)     # Admin privileges
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    rsvps = db.relationship('RSVP', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, first_name, last_name, is_admin=False):
        """
        Initialize user with required fields
        """
        self.username = username
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin
        # is_approved defaults to False - requires admin approval
        
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_authenticated(self):
        """Flask-Login required method"""
        return True
    
    def is_anonymous(self):
        """Flask-Login required method"""
        return False
        
    def get_id(self):
        """Flask-Login required method - return user ID as string"""
        return str(self.id)
    
    @property
    def full_name(self):
        """Return full name for display"""
        return f"{self.first_name} {self.last_name}"
    
    def can_login(self):
        """Check if user can login (active and approved)"""
        return self.is_active and self.is_approved
    
    def has_rsvp_for_event(self, event_id):
        """Check if user has RSVP'd for a specific event"""
        from .rsvp import RSVP
        return RSVP.query.filter_by(user_id=self.id, event_id=event_id).first() is not None
    
    def get_rsvp_for_event(self, event_id):
        """Get user's RSVP for a specific event"""
        from .rsvp import RSVP
        return RSVP.query.filter_by(user_id=self.id, event_id=event_id).first()
    
    @staticmethod
    def get_pending_users():
        """Get all users pending approval"""
        return User.query.filter_by(is_approved=False).order_by(User.created_at.desc()).all()
    
    @staticmethod
    def get_approved_users():
        """Get all approved users"""
        return User.query.filter_by(is_approved=True).order_by(User.first_name, User.last_name).all()
    
    def approve(self):
        """Approve user account"""
        self.is_approved = True
        db.session.commit()
    
    def deny(self):
        """Deny/deactivate user account"""
        self.is_approved = False
        self.is_active = False
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'
