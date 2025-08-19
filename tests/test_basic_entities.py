"""
Test Database Initialization and Basic Entity Creation
Tests basic functionality of User, Event, and RSVP models
"""
from datetime import datetime, timedelta


class TestDatabaseInitialization:
    """Test database creation and model imports"""
    
    def test_database_tables_created(self, db):
        """Test that all required database tables are created"""
        from models import User, Event, RSVP
        
        # Verify tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        expected_tables = ['users', 'events', 'rsvps']
        
        for table in expected_tables:
            assert table in tables, f'Table "{table}" should be created'
    
    def test_models_import_successfully(self):
        """Test that all models can be imported without errors"""
        from models import User, Event, RSVP
        
        # Verify models have required attributes
        assert hasattr(User, '__tablename__')
        assert hasattr(Event, '__tablename__')
        assert hasattr(RSVP, '__tablename__')


class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation(self, db):
        """Test basic user creation"""
        from models import User
        
        user = User(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.full_name == 'Test User'
        assert not user.is_approved  # Should default to False
        assert not user.is_admin     # Should default to False
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        from models import User
        
        user = User(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        
        # Password should be hashed
        assert user.password_hash != 'password123'
        
        # Password verification should work
        assert user.check_password('password123')
        assert not user.check_password('wrongpassword')
    
    def test_user_approval_status(self, admin_user, regular_user, pending_user):
        """Test user approval functionality"""
        # Admin should be able to login
        assert admin_user.can_login()
        assert admin_user.is_admin
        assert admin_user.is_approved
        
        # Regular approved user should be able to login
        assert regular_user.can_login()
        assert not regular_user.is_admin
        assert regular_user.is_approved
        
        # Pending user should not be able to login
        assert not pending_user.can_login()
        assert not pending_user.is_admin
        assert not pending_user.is_approved
    
    def test_user_queries(self, db, admin_user, regular_user, pending_user):
        """Test user query methods"""
        from models import User
        
        # Test pending users query
        pending_users = User.get_pending_users()
        assert len(pending_users) == 1
        assert pending_users[0].username == 'pendinguser'
        
        # Test approved users query
        approved_users = User.get_approved_users()
        assert len(approved_users) == 2  # admin and regular user
        approved_usernames = [user.username for user in approved_users]
        assert 'admin' in approved_usernames
        assert 'testuser' in approved_usernames


class TestEventModel:
    """Test Event model functionality"""
    
    def test_event_creation(self, db):
        """Test basic event creation"""
        from models import Event
        
        event_date = datetime.now() + timedelta(days=7)
        event = Event(
            title='Test Event',
            date_time=event_date,
            description='This is a test event',
            location='Test Location'
        )
        
        db.session.add(event)
        db.session.commit()
        
        assert event.id is not None
        assert event.title == 'Test Event'
        assert event.description == 'This is a test event'
        assert event.date_time == event_date
        assert event.location == 'Test Location'
    
    def test_event_past_future_detection(self, future_event, past_event):
        """Test event past/future detection methods"""
        assert not future_event.is_past
        assert past_event.is_past
    
    def test_upcoming_events_query(self, db, future_event):
        """Test query for upcoming events"""
        from models import Event
        
        upcoming_events = Event.get_upcoming_events()
        assert len(upcoming_events) == 1
        assert upcoming_events[0].title == 'Future Event'


class TestRSVPModel:
    """Test RSVP model functionality"""
    
    def test_rsvp_creation(self, regular_user, future_event):
        """Test basic RSVP creation"""
        from models import RSVP
        
        rsvp = RSVP.create(
            user_id=regular_user.id,
            event_id=future_event.id,
            status='attending'
        )
        
        assert rsvp.id is not None
        assert rsvp.user_id == regular_user.id
        assert rsvp.event_id == future_event.id
        assert rsvp.status == 'attending'
        assert rsvp.created_at is not None
    
    def test_rsvp_relationships(self, regular_user, future_event):
        """Test RSVP relationships with User and Event"""
        from models import RSVP
        
        rsvp = RSVP.create(
            user_id=regular_user.id,
            event_id=future_event.id,
            status='attending'
        )
        
        # Test relationships
        assert rsvp.user == regular_user
        assert rsvp.event == future_event
        assert rsvp in regular_user.rsvps
        assert rsvp in future_event.rsvps
    
    def test_rsvp_status_validation(self, regular_user, future_event):
        """Test RSVP status validation"""
        from models import RSVP
        
        # Test valid statuses - note: model uses 'attending' as default
        valid_statuses = ['attending', 'not_attending', 'maybe']
        
        for status in valid_statuses:
            rsvp = RSVP.create(
                user_id=regular_user.id,
                event_id=future_event.id,
                status=status
            )
            
            assert rsvp.status == status
            
            # Clean up for next iteration
            rsvp.delete()
    
    def test_user_rsvp_for_event(self, regular_user, future_event):
        """Test finding user's RSVP for specific event"""
        from models import RSVP
        
        # No RSVP initially
        rsvps = RSVP.get_user_rsvps(regular_user.id)
        event_rsvps = [r for r in rsvps if r.event_id == future_event.id]
        assert len(event_rsvps) == 0
        
        # Create RSVP using the create method
        new_rsvp = RSVP.create(
            user_id=regular_user.id,
            event_id=future_event.id,
            status='attending'
        )
        
        # Should find the RSVP
        rsvps = RSVP.get_user_rsvps(regular_user.id)
        event_rsvps = [r for r in rsvps if r.event_id == future_event.id]
        assert len(event_rsvps) == 1
        assert event_rsvps[0].id == new_rsvp.id
        assert event_rsvps[0].status == 'attending'


class TestEventRSVPIntegration:
    """Test integration between Events and RSVPs"""
    
    def test_event_rsvp_counts(self, future_event, regular_user, admin_user):
        """Test counting RSVPs for an event"""
        from models import RSVP
        
        # Create multiple RSVPs using the create method
        RSVP.create(user_id=regular_user.id, event_id=future_event.id, status='attending')
        RSVP.create(user_id=admin_user.id, event_id=future_event.id, status='not_attending')
        
        # Test attendee count (only 'attending' status)
        assert future_event.get_attendee_count() == 1
        
        # Test total RSVPs
        event_rsvps = RSVP.get_event_rsvps(future_event.id)
        assert len(event_rsvps) == 2
    
    def test_event_attendee_list(self, future_event, regular_user, admin_user):
        """Test getting list of attendees for an event"""
        from models import RSVP
        
        # Create RSVPs using the create method
        RSVP.create(user_id=regular_user.id, event_id=future_event.id, status='attending')
        RSVP.create(user_id=admin_user.id, event_id=future_event.id, status='not_attending')
        
        # Test attendee lists (only attending users)
        attending = future_event.get_attendees()
        
        assert len(attending) == 1
        assert attending[0].username == 'testuser'

