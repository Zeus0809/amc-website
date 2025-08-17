"""
Event model for AMC Website
Handles event creation, management and relationships
"""
from datetime import datetime
from .database import db, generate_uuid

class Event(db.Model):
    """
    Event model for storing event information
    """
    __tablename__ = 'events'
    
    # Primary key - UUID for security
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    
    # Event information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    max_attendees = db.Column(db.Integer, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Relationships - Events connect to Users through RSVP join table
    rsvps = db.relationship('RSVP', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, title, date_time, description=None, location=None, max_attendees=None):
        """
        Initialize event with required fields
        """
        self.title = title
        self.date_time = date_time
        self.description = description
        self.location = location
        self.max_attendees = max_attendees
    
    @property
    def is_past(self):
        """Check if event is in the past"""
        return datetime.now() > self.date_time
    
    @property
    def formatted_date(self):
        """Return formatted date string for display"""
        return self.date_time.strftime('%A, %B %d, %Y')
    
    @property
    def formatted_time(self):
        """Return formatted time string for display"""
        return self.date_time.strftime('%I:%M %p')
    
    @property
    def formatted_datetime(self):
        """Return formatted date and time string"""
        return self.date_time.strftime('%A, %B %d, %Y at %I:%M %p')
    
    def get_attendee_count(self):
        """Get count of users who RSVP'd as attending"""
        from .rsvp import RSVP
        return RSVP.query.filter_by(event_id=self.id, status='attending').count()
    
    def get_attendees(self):
        """Get list of users who RSVP'd as attending"""
        from .rsvp import RSVP
        from .user import User
        rsvp_user_ids = db.session.query(RSVP.user_id).filter_by(event_id=self.id, status='attending').all()
        user_ids = [row[0] for row in rsvp_user_ids]
        return User.query.filter(User.id.in_(user_ids)).order_by(User.first_name, User.last_name).all()
    
    def is_full(self):
        """Check if event has reached max capacity"""
        if self.max_attendees is None:
            return False
        return self.get_attendee_count() >= self.max_attendees
    
    def can_rsvp(self, user):
        """Check if user can RSVP to this event"""
        # Can't RSVP to past events
        if self.is_past:
            return False
        
        # Can't RSVP if event is full
        if self.is_full():
            return False
        
        # Can't RSVP if user already has an RSVP
        if user.has_rsvp_for_event(self.id):
            return False
        
        return True
    
    @staticmethod
    def get_upcoming_events():
        """Get all upcoming events ordered by date"""
        return Event.query.filter(Event.date_time > datetime.now()).order_by(Event.date_time).all()
    
    @staticmethod
    def get_past_events():
        """Get all past events ordered by date (most recent first)"""
        return Event.query.filter(Event.date_time <= datetime.now()).order_by(Event.date_time.desc()).all()
    
    @staticmethod
    def get_all_events():
        """Get all events ordered by date (upcoming first, then past)"""
        upcoming = Event.get_upcoming_events()
        past = Event.get_past_events()
        return upcoming + past
    
    def __repr__(self):
        return f'<Event {self.title} on {self.formatted_date}>'
