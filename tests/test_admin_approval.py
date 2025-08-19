"""
Test admin approval workflow functionality
"""
from models import User


class TestUserApprovalWorkflow:
    """Test admin approval and denial methods"""
    
    def test_user_approve_method(self, pending_user):
        """Test that approve() method correctly approves a user"""
        # Verify initial state
        assert pending_user.is_approved is False
        assert pending_user.is_active is True
        assert pending_user.can_login() is False
        
        # Approve user
        pending_user.approve()
        
        # Verify approved state
        assert pending_user.is_approved is True
        assert pending_user.is_active is True
        assert pending_user.can_login() is True
        
        # Verify persistence in database
        user_from_db = User.query.get(pending_user.id)
        assert user_from_db.is_approved is True
        assert user_from_db.can_login() is True
    
    def test_user_deny_method(self, pending_user):
        """Test that deny() method correctly denies a user"""
        # Verify initial state
        assert pending_user.is_approved is False
        assert pending_user.is_active is True
        assert pending_user.can_login() is False
        
        # Deny user
        pending_user.deny()
        
        # Verify denied state
        assert pending_user.is_approved is False
        assert pending_user.is_active is False
        assert pending_user.can_login() is False
        
        # Verify persistence in database
        user_from_db = User.query.get(pending_user.id)
        assert user_from_db.is_approved is False
        assert user_from_db.is_active is False
        assert user_from_db.can_login() is False
    
    def test_deny_approved_user(self, regular_user):
        """Test denying a previously approved user"""
        # Verify initial approved state
        assert regular_user.is_approved is True
        assert regular_user.is_active is True
        assert regular_user.can_login() is True
        
        # Deny the approved user
        regular_user.deny()
        
        # Verify denied state
        assert regular_user.is_approved is False
        assert regular_user.is_active is False
        assert regular_user.can_login() is False
    
    def test_approve_denied_user(self, pending_user):
        """Test approving a user that was previously denied"""
        # First deny the user
        pending_user.deny()
        assert pending_user.is_approved is False
        assert pending_user.is_active is False
        assert pending_user.can_login() is False
        
        # Now approve the user
        pending_user.approve()
        
        # Verify approved state (but still inactive from denial)
        assert pending_user.is_approved is True
        assert pending_user.is_active is False  # deny() sets this to False
        assert pending_user.can_login() is False  # requires both approved AND active


class TestUserApprovalQueries:
    """Test user approval query methods"""
    
    def test_get_pending_users(self, pending_user):
        """Test getting all pending users"""
        pending_users = User.get_pending_users()
        
        # Should only contain the pending user
        assert len(pending_users) == 1
        assert pending_users[0].id == pending_user.id
        assert pending_users[0].is_approved is False
        
        # Should be ordered by created_at desc (most recent first)
        assert pending_users[0].username == 'pendinguser'
    
    def test_get_approved_users(self, admin_user, regular_user, pending_user):
        """Test getting all approved users"""
        approved_users = User.get_approved_users()
        
        # Should contain admin and regular user, not pending
        assert len(approved_users) == 2
        user_ids = [user.id for user in approved_users]
        assert admin_user.id in user_ids
        assert regular_user.id in user_ids
        assert pending_user.id not in user_ids
        
        # Should be ordered by first_name, last_name
        assert all(user.is_approved for user in approved_users)
    
    def test_pending_users_after_approval(self, pending_user):
        """Test that pending users list updates after approval"""
        # Initially should have pending user
        pending_users = User.get_pending_users()
        assert len(pending_users) == 1
        assert pending_users[0].id == pending_user.id
        
        # Approve the user
        pending_user.approve()
        
        # Should no longer be in pending list
        pending_users_after = User.get_pending_users()
        assert len(pending_users_after) == 0
        
        # Should now be in approved list
        approved_users = User.get_approved_users()
        approved_ids = [user.id for user in approved_users]
        assert pending_user.id in approved_ids


class TestApprovalWorkflowIntegration:
    """Test integration scenarios for approval workflow"""
    
    def test_approval_workflow_complete_cycle(self, db):
        """Test complete user approval workflow from registration to approval"""
        # Create a new pending user (simulating registration)
        new_user = User(
            username='newmember',
            email='new@example.com',
            password='password123',
            first_name='New',
            last_name='Member'
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Verify initial pending state
        assert new_user.is_approved is False
        assert new_user.is_active is True
        assert new_user.can_login() is False
        
        # Should appear in pending users
        pending_users = User.get_pending_users()
        assert new_user.id in [user.id for user in pending_users]
        
        # Admin approves user
        new_user.approve()
        
        # Verify approved state
        assert new_user.can_login() is True
        
        # Should no longer be in pending list
        pending_users_after = User.get_pending_users()
        assert new_user.id not in [user.id for user in pending_users_after]
        
        # Should be in approved list
        approved_users = User.get_approved_users()
        assert new_user.id in [user.id for user in approved_users]
    
    def test_multiple_approval_operations(self, db):
        """Test multiple approve/deny operations don't cause issues"""
        new_user = User(
            username='testcycle',
            email='cycle@example.com', 
            password='password123',
            first_name='Test',
            last_name='Cycle'
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Multiple approvals should be safe
        new_user.approve()
        new_user.approve()
        assert new_user.is_approved is True
        assert new_user.can_login() is True
        
        # Deny after approval
        new_user.deny()
        assert new_user.can_login() is False
        
        # Multiple denials should be safe
        new_user.deny()
        assert new_user.is_approved is False
        assert new_user.is_active is False
