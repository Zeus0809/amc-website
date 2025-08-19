"""
Pytest configuration and shared fixtures for AMC Website tests
"""
import os
import sys
import tempfile
import pytest
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='function')
def app():
    """Create a Flask app configured for testing"""
    from app import create_app
    
    # Create app with testing configuration
    app = create_app('testing')
    
    yield app


@pytest.fixture(scope='function')
def app_context(app):
    """Create an application context for testing"""
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db(app_context):
    """Create database tables for testing"""
    from models import db as _db
    
    # Create all tables
    _db.create_all()
    
    yield _db
    
    # Clean up
    _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for making HTTP requests"""
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='function')
def admin_user(db):
    """Create an admin user for testing"""
    from models import User
    
    admin = User(
        username='admin',
        email='admin@test.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        is_admin=True
    )
    admin.is_approved = True  # Set after creation
    
    db.session.add(admin)
    db.session.commit()
    
    return admin


@pytest.fixture(scope='function')
def regular_user(db):
    """Create a regular approved user for testing"""
    from models import User
    
    user = User(
        username='testuser',
        email='user@test.com',
        password='password123',
        first_name='Test',
        last_name='User'
    )
    user.is_approved = True  # Set after creation
    
    db.session.add(user)
    db.session.commit()
    
    return user


@pytest.fixture(scope='function')
def pending_user(db):
    """Create a pending (unapproved) user for testing"""
    from models import User
    
    user = User(
        username='pendinguser',
        email='pending@test.com',
        password='password123',
        first_name='Pending',
        last_name='User'
        # is_approved defaults to False
    )
    
    db.session.add(user)
    db.session.commit()
    
    return user


@pytest.fixture(scope='function')
def future_event(db):
    """Create a future event for testing"""
    from models import Event
    
    event = Event(
        title='Future Event',
        date_time=datetime.now() + timedelta(days=7),
        description='This is a future event for testing',
        location='Test Location'
    )
    
    db.session.add(event)
    db.session.commit()
    
    return event


@pytest.fixture(scope='function')
def past_event(db):
    """Create a past event for testing"""
    from models import Event
    
    event = Event(
        title='Past Event',
        date_time=datetime.now() - timedelta(days=7),
        description='This is a past event for testing',
        location='Test Location'
    )
    
    db.session.add(event)
    db.session.commit()
    
    return event
