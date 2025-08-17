"""
Test Database Initialization and Basic Entity Creation
Tests basic functionality of User, Event, and RSVP models
"""
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_initialization():
    """Test database creation and model imports"""
    print('=== Testing Database Initialization ===\n')
    
    # Set up test database path in temp directory
    import tempfile
    test_db_path = os.path.join(tempfile.gettempdir(), 'test_basic.db')
    os.environ['DEV_DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    try:
        from app import app
        with app.app_context():
            from models import db, User, Event, RSVP
            
            # Clean start
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            
            # Create tables
            db.create_all()
            print('✅ Database tables created successfully')
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            expected_tables = ['users', 'events', 'rsvps']
            
            for table in expected_tables:
                if table in tables:
                    print(f'✅ Table "{table}" created')
                else:
                    print(f'❌ Table "{table}" missing')
                    return False
            
            return True
            
    except Exception as e:
        print(f'❌ Database initialization failed: {e}')
        return False
    finally:
        # Clean up
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

def test_user_model():
    """Test User model creation and methods"""
    print('\n=== Testing User Model ===\n')
    
    import tempfile
    test_db_path = os.path.join(tempfile.gettempdir(), 'test_user.db')
    os.environ['DEV_DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    try:
        from app import app
        with app.app_context():
            from models import db, User
            
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            
            db.create_all()
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@test.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.is_approved = True
            
            # Create regular user
            user = User(
                username='testuser',
                email='user@test.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            
            db.session.add_all([admin, user])
            db.session.commit()
            
            # Test user properties
            print(f'✅ Admin created: {admin.full_name}')
            print(f'   - Can login: {admin.can_login()}')
            print(f'   - Is admin: {admin.is_admin}')
            
            print(f'✅ Regular user created: {user.full_name}')
            print(f'   - Can login: {user.can_login()}')
            print(f'   - Is approved: {user.is_approved}')
            
            # Test password verification
            if admin.check_password('admin123'):
                print('✅ Admin password verification works')
            else:
                print('❌ Admin password verification failed')
                return False
            
            if user.check_password('password123'):
                print('✅ User password verification works')
            else:
                print('❌ User password verification failed')
                return False
            
            # Test user queries
            pending_users = User.get_pending_users()
            approved_users = User.get_approved_users()
            
            print(f'✅ Pending users: {len(pending_users)}')
            print(f'✅ Approved users: {len(approved_users)}')
            
            return True
            
    except Exception as e:
        print(f'❌ User model test failed: {e}')
        return False
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

def test_event_model():
    """Test Event model creation and methods"""
    print('\n=== Testing Event Model ===\n')
    
    import tempfile
    test_db_path = os.path.join(tempfile.gettempdir(), 'test_event.db')
    os.environ['DEV_DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    try:
        from app import app
        with app.app_context():
            from models import db, Event
            
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            
            db.create_all()
            
            # Create future event
            future_event = Event(
                title='Future AMC Meeting',
                date_time=datetime.now() + timedelta(days=14),
                description='Upcoming club meeting',
                location='Club House',
                max_attendees=50
            )
            
            # Create past event
            past_event = Event(
                title='Past AMC Meeting',
                date_time=datetime.now() - timedelta(days=7),
                description='Previous meeting',
                location='Club House'
            )
            
            db.session.add_all([future_event, past_event])
            db.session.commit()
            
            # Test event properties
            print(f'✅ Future event: {future_event.title}')
            print(f'   - Is past: {future_event.is_past}')
            print(f'   - Formatted date: {future_event.formatted_date}')
            print(f'   - Attendee count: {future_event.get_attendee_count()}')
            
            print(f'✅ Past event: {past_event.title}')
            print(f'   - Is past: {past_event.is_past}')
            
            # Test static methods
            upcoming_events = Event.get_upcoming_events()
            past_events = Event.get_past_events()
            
            print(f'✅ Upcoming events: {len(upcoming_events)}')
            print(f'✅ Past events: {len(past_events)}')
            
            return True
            
    except Exception as e:
        print(f'❌ Event model test failed: {e}')
        return False
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

def test_rsvp_model():
    """Test RSVP model and relationships"""
    print('\n=== Testing RSVP Model ===\n')
    
    import tempfile
    test_db_path = os.path.join(tempfile.gettempdir(), 'test_rsvp.db')
    os.environ['DEV_DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    try:
        from app import app
        with app.app_context():
            from models import db, User, Event, RSVP
            
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            
            db.create_all()
            
            # Create user and event
            user = User(
                username='testuser',
                email='test@test.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            user.is_approved = True
            
            event = Event(
                title='Test Event',
                date_time=datetime.now() + timedelta(days=7),
                description='Test event for RSVP'
            )
            
            db.session.add_all([user, event])
            db.session.commit()
            
            # Test RSVP creation
            rsvp = RSVP.create(user.id, event.id, 'attending')
            
            if rsvp:
                print('✅ RSVP created successfully')
                print(f'   - Status: {rsvp.status}')
                print(f'   - Is attending: {rsvp.is_attending}')
            else:
                print('❌ RSVP creation failed')
                return False
            
            # Test attendee count
            print(f'✅ Event attendee count: {event.get_attendee_count()}')
            
            # Test duplicate prevention
            try:
                duplicate_rsvp = RSVP.create(user.id, event.id, 'maybe')
                print('❌ ERROR: Duplicate RSVP should have been prevented')
                return False
            except ValueError as e:
                print(f'✅ Duplicate prevention works: {e}')
            
            # Test status update
            if rsvp.update_status('maybe'):
                print('✅ RSVP status update successful')
                print(f'   - Updated attendee count: {event.get_attendee_count()}')
            else:
                print('❌ RSVP status update failed')
                return False
            
            return True
            
    except Exception as e:
        print(f'❌ RSVP model test failed: {e}')
        return False
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

def run_all_tests():
    """Run all basic entity tests"""
    print('🧪 AMC Website - Basic Entity Tests\n')
    print('=' * 50)
    
    tests = [
        test_database_initialization,
        test_user_model,
        test_event_model,
        test_rsvp_model
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f'\n✅ {test.__name__} PASSED')
            else:
                failed += 1
                print(f'\n❌ {test.__name__} FAILED')
        except Exception as e:
            failed += 1
            print(f'\n❌ {test.__name__} FAILED with exception: {e}')
        
        print('-' * 50)
    
    print(f'\n🎉 Test Summary: {passed} passed, {failed} failed')
    
    if failed == 0:
        print('✅ All basic entity tests PASSED!')
        return True
    else:
        print('❌ Some tests FAILED!')
        return False

if __name__ == '__main__':
    run_all_tests()
