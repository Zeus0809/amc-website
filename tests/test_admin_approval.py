"""
Test Admin Approval Process
Tests the complete user registration and admin approval workflow
"""
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_user_registration_flow():
    """Test new user registration defaults"""
    print('=== Testing User Registration Flow ===\n')
    
    import tempfile
    test_db_path = os.path.join(tempfile.gettempdir(), 'test_registration.db')
    os.environ['DEV_DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    try:
        from app import app
        with app.app_context():
            from models import db, User
            
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            
            db.create_all()
            
            # Simulate new user registration
            new_user = User(
                username='newuser',
                email='newuser@email.com',
                password='password123',
                first_name='New',
                last_name='User'
            )
            # Don't set is_approved - should default to False
            
            db.session.add(new_user)
            db.session.commit()
            
            print(f'✅ New user registered: {new_user.full_name}')
            print(f'   - Username: {new_user.username}')
            print(f'   - Email: {new_user.email}')
            print(f'   - Is approved: {new_user.is_approved}')
            print(f'   - Is admin: {new_user.is_admin}')
            print(f'   - Can login: {new_user.can_login()}')
            
            if not new_user.is_approved and not new_user.can_login():
                print('✅ New user correctly starts unapproved and cannot login')
                return True
            else:
                print('❌ New user should be unapproved and unable to login')
                return False
                
    except Exception as e:
        print(f'❌ Registration flow test failed: {e}')
        return False
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

def test_admin_creation():
    """Test admin user creation and privileges"""
    print('\n=== Testing Admin Creation ===\n')
    
    import tempfile
    test_db_path = os.path.join(tempfile.gettempdir(), 'test_admin.db')
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
                email='admin@amc.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.is_approved = True  # Admin should be auto-approved
            
            db.session.add(admin)
            db.session.commit()
            
            print(f'✅ Admin user created: {admin.full_name}')
            print(f'   - Is admin: {admin.is_admin}')
            print(f'   - Is approved: {admin.is_approved}')
            print(f'   - Can login: {admin.can_login()}')
            
            if admin.is_admin and admin.is_approved and admin.can_login():
                print('✅ Admin has correct privileges and can login')
                return True
            else:
                print('❌ Admin should have privileges and login access')
                return False
                
    except Exception as e:
        print(f'❌ Admin creation test failed: {e}')
        return False
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

def test_approval_process():
    """Test the complete admin approval workflow"""
    print('\n=== Testing Admin Approval Process ===\n')
    
    import tempfile
    test_db_path = os.path.join(tempfile.gettempdir(), 'test_approval.db')
    os.environ['DEV_DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    try:
        from app import app
        with app.app_context():
            from models import db, User
            
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            
            db.create_all()
            
            # Create admin
            admin = User(
                username='admin',
                email='admin@amc.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.is_approved = True
            
            # Create pending user
            pending_user = User(
                username='pending',
                email='pending@email.com',
                password='password123',
                first_name='Pending',
                last_name='User'
            )
            
            db.session.add_all([admin, pending_user])
            db.session.commit()
            
            print('👑 Initial State:')
            print(f'   Admin can login: {admin.can_login()}')
            print(f'   Pending user can login: {pending_user.can_login()}')
            
            # Test approval process
            print(f'\n📋 Admin approving user "{pending_user.username}"...')
            pending_user.approve()
            db.session.commit()
            
            print('✅ Approval completed')
            print(f'   Pending user approved status: {pending_user.is_approved}')
            print(f'   Pending user can now login: {pending_user.can_login()}')
            
            if pending_user.is_approved and pending_user.can_login():
                print('✅ Approval process works correctly')
                return True
            else:
                print('❌ Approval process failed')
                return False
                
    except Exception as e:
        print(f'❌ Approval process test failed: {e}')
        return False
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

def test_pending_users_management():
    """Test admin dashboard queries for user management"""
    print('\n=== Testing Pending Users Management ===\n')
    
    import tempfile
    test_db_path = os.path.join(tempfile.gettempdir(), 'test_management.db')
    os.environ['DEV_DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    try:
        from app import app
        with app.app_context():
            from models import db, User
            
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            
            db.create_all()
            
            # Create mix of users
            admin = User(
                username='admin',
                email='admin@amc.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.is_approved = True
            
            approved_user = User(
                username='approved',
                email='approved@email.com',
                password='password123',
                first_name='Approved',
                last_name='User'
            )
            approved_user.approve()
            
            pending_user1 = User(
                username='pending1',
                email='pending1@email.com',
                password='password123',
                first_name='Pending1',
                last_name='User'
            )
            
            pending_user2 = User(
                username='pending2',
                email='pending2@email.com',
                password='password123',
                first_name='Pending2',
                last_name='User'
            )
            
            db.session.add_all([admin, approved_user, pending_user1, pending_user2])
            db.session.commit()
            
            # Test admin queries
            pending_users = User.get_pending_users()
            approved_users = User.get_approved_users()
            
            print(f'📊 User Management Summary:')
            print(f'   Total pending users: {len(pending_users)}')
            for user in pending_users:
                print(f'     - {user.full_name} ({user.email})')
            
            print(f'   Total approved users: {len(approved_users)}')
            for user in approved_users:
                print(f'     - {user.full_name} ({user.email}) [Admin: {user.is_admin}]')
            
            # Validate counts
            if len(pending_users) == 2 and len(approved_users) == 2:
                print('✅ User management queries work correctly')
                return True
            else:
                print(f'❌ Expected 2 pending and 2 approved, got {len(pending_users)} pending and {len(approved_users)} approved')
                return False
                
    except Exception as e:
        print(f'❌ User management test failed: {e}')
        return False
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

def test_access_control():
    """Test that approval controls access properly"""
    print('\n=== Testing Access Control ===\n')
    
    import tempfile
    test_db_path = os.path.join(tempfile.gettempdir(), 'test_access.db')
    os.environ['DEV_DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    try:
        from app import app
        with app.app_context():
            from models import db, User, Event
            
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
            
            db.create_all()
            
            # Create users
            approved_user = User(
                username='approved',
                email='approved@test.com',
                password='password123',
                first_name='Approved',
                last_name='User'
            )
            approved_user.approve()
            
            unapproved_user = User(
                username='unapproved',
                email='unapproved@test.com',
                password='password123',
                first_name='Unapproved',
                last_name='User'
            )
            
            # Create event
            event = Event(
                title='Test Event',
                date_time=datetime.now() + timedelta(days=5),
                description='Test event for access control'
            )
            
            db.session.add_all([approved_user, unapproved_user, event])
            db.session.commit()
            
            print('🔐 Access Control Test:')
            print(f'   Approved user can login: {approved_user.can_login()}')
            print(f'   Unapproved user can login: {unapproved_user.can_login()}')
            
            # The key test: only approved users should be able to login
            # RSVP access will be controlled by login requirement in routes
            if approved_user.can_login() and not unapproved_user.can_login():
                print('✅ Access control working - login restricted to approved users')
                return True
            else:
                print('❌ Access control failed')
                return False
                
    except Exception as e:
        print(f'❌ Access control test failed: {e}')
        return False
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

def run_approval_tests():
    """Run all admin approval workflow tests"""
    print('🔑 AMC Website - Admin Approval Workflow Tests\n')
    print('=' * 60)
    
    tests = [
        test_user_registration_flow,
        test_admin_creation,
        test_approval_process,
        test_pending_users_management,
        test_access_control
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
        
        print('-' * 60)
    
    print(f'\n🎉 Test Summary: {passed} passed, {failed} failed')
    
    if failed == 0:
        print('✅ All admin approval workflow tests PASSED!')
        print('🔑 User registration and approval system ready for production!')
        return True
    else:
        print('❌ Some approval workflow tests FAILED!')
        return False

if __name__ == '__main__':
    run_approval_tests()
