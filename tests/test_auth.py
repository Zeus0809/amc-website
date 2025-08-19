"""
Tests for authentication system - forms, registration, login, and admin functionality.
"""
from flask import url_for
from models import User, db
from werkzeug.security import check_password_hash


class TestAuthForms:
    """Test authentication form validation."""
    
    def test_login_form_validation(self, client):
        """Test login form requires username and password."""
        response = client.post('/login', data={})
        assert b'Username is required' in response.data
        assert b'Password is required' in response.data
        
    def test_registration_form_validation(self, client, db):
        """Test registration form validates all required fields."""
        # Missing fields
        response = client.post('/register', data={})
        assert response.status_code == 200
        assert b'Username is required' in response.data
        
        # Password mismatch
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'password123',
            'password_confirm': 'differentpassword'
        })
        assert b'Passwords must match' in response.data

    def test_username_length_validation(self, client, db):
        """Test username length requirements."""
        # Too short
        response = client.post('/register', data={
            'username': 'ab',  # Only 2 characters
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        assert b'Username must be 3-50 characters' in response.data
    
    def test_password_length_validation(self, client, db):
        """Test password minimum length requirement."""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': '12345',  # Only 5 characters
            'password_confirm': '12345'
        })
        assert b'Password must be at least 6 characters' in response.data
    
    def test_email_format_validation(self, client, db):
        """Test email format validation."""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'invalid-email',  # Invalid format
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        assert b'Please enter a valid email address' in response.data


class TestUserRegistration:
    """Test user registration workflow."""
    
    def test_new_user_registration(self, client, app, db):
        """Test new user can register and is pending approval."""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'password_confirm': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'pending administrator approval' in response.data
        
        # Check user was created in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.is_approved is False
            assert check_password_hash(user.password_hash, 'password123')
    
    def test_duplicate_username_rejected(self, client, regular_user):
        """Test registration fails with duplicate username."""
        response = client.post('/register', data={
            'username': regular_user.username,  # Duplicate
            'email': 'different@example.com',
            'first_name': 'Different',
            'last_name': 'User',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        
        assert b'Username already exists' in response.data
    
    def test_duplicate_email_rejected(self, client, regular_user):
        """Test registration fails with duplicate email."""
        response = client.post('/register', data={
            'username': 'differentuser',
            'email': regular_user.email,  # Duplicate
            'first_name': 'Different',
            'last_name': 'User',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        
        assert b'Email already registered' in response.data


class TestUserLogin:
    """Test user login authentication."""
    
    def test_approved_user_login_success(self, client, regular_user):
        """Test approved user can login successfully."""
        response = client.post('/login', data={
            'username': regular_user.username,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome to the AMC website' in response.data
    
    def test_unapproved_user_redirected_to_pending(self, client, pending_user):
        """Test unapproved user gets redirected to pending page."""
        response = client.post('/login', data={
            'username': pending_user.username,
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'pending administrator approval' in response.data
    
    def test_invalid_credentials_rejected(self, client, regular_user):
        """Test invalid credentials are rejected."""
        response = client.post('/login', data={
            'username': regular_user.username,
            'password': 'wrongpassword'
        })
        
        assert b'Invalid username or password' in response.data
    
    def test_nonexistent_user_rejected(self, client, db):
        """Test login with nonexistent username is rejected."""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert b'Invalid username or password' in response.data
    
    def test_inactive_user_rejected(self, client, app, db):
        """Test inactive user cannot login."""
        with app.app_context():
            user = User(
                username='inactive',
                email='inactive@example.com',
                password='password123',
                first_name='Inactive',
                last_name='User'
            )
            user.is_approved = True
            user.is_active = False
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'username': 'inactive',
            'password': 'password123'
        })
        
        assert b'account has been deactivated' in response.data


class TestAdminAuthorization:
    """Test admin-only functionality."""
    
    def test_admin_can_access_admin_routes(self, client, admin_user):
        """Test admin user can access admin routes."""
        # Login as admin
        client.post('/login', data={
            'username': admin_user.username,
            'password': 'admin123'
        })
        
        response = client.get('/admin/users')
        assert response.status_code == 200
    
    def test_regular_user_blocked_from_admin_routes(self, client, regular_user):
        """Test regular user cannot access admin routes."""
        # Login as regular user
        client.post('/login', data={
            'username': regular_user.username,
            'password': 'password123'
        })
        
        response = client.get('/admin/users')
        assert response.status_code == 403
    
    def test_unauthenticated_user_blocked_from_admin_routes(self, client):
        """Test unauthenticated user cannot access admin routes."""
        response = client.get('/admin/users')
        assert response.status_code == 302  # Redirect to login
    
    def test_admin_can_approve_users(self, client, admin_user, pending_user):
        """Test admin can approve pending users."""
        # Login as admin
        client.post('/login', data={
            'username': admin_user.username,
            'password': 'admin123'
        })
        
        response = client.get(f'/admin/approve-user/{pending_user.id}', 
                            follow_redirects=True)
        assert response.status_code == 200
        assert b'has been approved!' in response.data
        
        # Check user is now approved
        db.session.refresh(pending_user)
        assert pending_user.is_approved is True
    
    def test_admin_can_deny_users(self, client, admin_user, pending_user):
        """Test admin can deny/deactivate users."""
        # Login as admin
        client.post('/login', data={
            'username': admin_user.username,
            'password': 'admin123'
        })
        
        response = client.get(f'/admin/deny-user/{pending_user.id}', 
                            follow_redirects=True)
        assert response.status_code == 200
        assert b'has been denied/deactivated.' in response.data
        
        # Check user is now denied and inactive
        db.session.refresh(pending_user)
        assert pending_user.is_approved is False
        assert pending_user.is_active is False


class TestSessionManagement:
    """Test login/logout and session handling."""
    
    def test_logout_functionality(self, client, regular_user):
        """Test user can logout successfully."""
        # Login first
        client.post('/login', data={
            'username': regular_user.username,
            'password': 'password123'
        })
        
        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'You have been logged out' in response.data
    
    def test_approved_user_redirected_from_login_when_logged_in(self, client, regular_user):
        """Test already logged in approved user gets redirected from login page."""
        # Login first
        client.post('/login', data={
            'username': regular_user.username,
            'password': 'password123'
        })
        
        # Try to access login page again
        response = client.get('/login', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected to events page
        assert b'events' in response.data.lower() or b'Events' in response.data
    
    def test_unapproved_user_redirected_to_pending_when_logged_in(self, client, pending_user):
        """Test already logged in but unapproved user gets redirected to pending page."""
        # Login as unapproved user
        client.post('/login', data={
            'username': pending_user.username,
            'password': 'password123'
        })
        
        # Try to access login page again
        response = client.get('/login', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected to pending approval page
        assert b'pending administrator approval' in response.data
    
    def test_pending_approval_page_redirects_approved_users(self, client, regular_user):
        """Test that approved users are redirected away from pending approval page."""
        # Login
        client.post('/login', data={
            'username': regular_user.username,
            'password': 'password123'
        })
        
        # Try to access pending approval page
        response = client.get('/pending', follow_redirects=True)
        assert response.status_code == 200
        # Should be redirected away from pending page
        assert b'pending administrator approval' not in response.data


class TestPasswordSecurity:
    """Test password hashing and security."""
    
    def test_password_is_hashed(self, app, db):
        """Test that passwords are properly hashed."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='plaintext123',
                first_name='Test',
                last_name='User'
            )
            db.session.add(user)
            db.session.commit()
            
            # Password should be hashed, not stored as plaintext
            assert user.password_hash != 'plaintext123'
            assert len(user.password_hash) > 50  # Hash should be much longer
            
            # Should be able to verify with check_password_hash
            assert check_password_hash(user.password_hash, 'plaintext123')
            assert not check_password_hash(user.password_hash, 'wrongpassword')
    
    def test_case_insensitive_username_login(self, client, regular_user):
        """Test that username login is case-insensitive."""
        # Try logging in with different case
        response = client.post('/login', data={
            'username': regular_user.username.upper(),
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome to the AMC website' in response.data

    
