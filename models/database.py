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
    
    # Import all models here to ensure they are registered with SQLAlchemy
    from .user import User
    from .event import Event
    from .rsvp import RSVP
    
    # Create all tables in app context
    with app.app_context():
        try:
            # Ensure instance directory exists for SQLite databases
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            
            if db_uri.startswith('sqlite:///'):
                # Extract the actual file path from SQLite URI
                db_path = db_uri.replace('sqlite:///', '')
                
                # Convert to absolute path if it's relative
                if not os.path.isabs(db_path):
                    db_path = os.path.abspath(db_path)
                
                db_dir = os.path.dirname(db_path)
                
                if db_dir:  # Only create directory if there is one
                    os.makedirs(db_dir, exist_ok=True)
            
            # Create all tables
            db.create_all()
            print(f"✅ Database tables created/verified for {app.config.get('ENV', 'development')} environment")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
            raise

def generate_uuid():
    """Generate UUID for primary keys (SQLite compatible)"""
    return str(uuid.uuid4())
