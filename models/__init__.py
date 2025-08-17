"""
Models package for AMC Website
Imports all database models and database configuration
"""

# Import database configuration
from .database import db, migrate, init_db

# Import all models
from .user import User
from .event import Event
from .rsvp import RSVP

# Make models available at package level:
# It's like putting a sign on your package that says: "These are the only things I want you to use from this package."
__all__ = ['db', 'migrate', 'init_db', 'User', 'Event', 'RSVP']
