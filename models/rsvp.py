"""
RSVP model for AMC Website
Handles user RSVPs to events - junction table between Users and Events
"""
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from .database import db, generate_uuid

class RSVP(db.Model):
    """
    RSVP model - junction table between Users and Events
    """
    __tablename__ = 'rsvps'
    
    # Primary key - UUID for security
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    
    # Foreign keys
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.String(36), db.ForeignKey('events.id'), nullable=False)
    
    # RSVP status
    status = db.Column(db.String(20), default='attending', nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Unique constraint - one RSVP per user per event
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='unique_user_event_rsvp'),
    )
    
    def __init__(self, user_id, event_id, status='attending'):
        """
        Initialize RSVP with required fields
        """
        self.user_id = user_id
        self.event_id = event_id
        self.status = status
    
    @property
    def is_attending(self):
        """Check if RSVP status is attending"""
        return self.status == 'attending'
    
    @classmethod
    def create(cls, user_id, event_id, status='attending'):
        """
        Create a new RSVP - database constraint ensures uniqueness
        Raises ValueError if user already has RSVP for this event
        """
        try:
            new_rsvp = cls(user_id=user_id, event_id=event_id, status=status)
            db.session.add(new_rsvp)
            db.session.commit()
            return new_rsvp
        except IntegrityError:
            db.session.rollback()
            raise ValueError(f"User already has an RSVP for this event")
    
    def update_status(self, status):
        """
        Update this RSVP's status
        """
        self.status = status
        db.session.commit()
    
    def delete(self):
        """
        Delete this RSVP
        """
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_user_rsvps(user_id):
        """Get all RSVPs for a specific user"""
        return RSVP.query.filter_by(user_id=user_id).order_by(RSVP.created_at.desc()).all()
    
    @staticmethod
    def get_event_rsvps(event_id):
        """Get all RSVPs for a specific event"""
        return RSVP.query.filter_by(event_id=event_id).order_by(RSVP.created_at).all()
    
    def __repr__(self):
        return f'<RSVP {self.user_id} -> {self.event_id} ({self.status})>'
