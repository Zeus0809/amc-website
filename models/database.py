"""
Database configuration and setup for AMC Website
"""
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid

# Initialize SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Ensure instance directory exists for SQLite
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    
    # Import all models here to ensure they are registered with SQLAlchemy
    from .user import User
    from .event import Event
    from .rsvp import RSVP
    
    # Don't create tables automatically - let the developer do it manually
    # This prevents issues during app initialization

def generate_uuid():
    """Generate UUID for primary keys (SQLite compatible)"""
    return str(uuid.uuid4())
