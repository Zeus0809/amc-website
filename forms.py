"""
Flask-WTF forms for authentication and user management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired, 
    Email, 
    Length, 
    EqualTo, 
    ValidationError
)
from models import User


class LoginForm(FlaskForm):
    """User login form."""
    username = StringField(
        'Username', 
        validators=[
            DataRequired(message="Username is required"),
            Length(min=3, max=50, message="Username must be 3-50 characters")
        ]
    )
    password = PasswordField(
        'Password', 
        validators=[
            DataRequired(message="Password is required"),
            Length(min=6, max=50, message="Password must be 6-50 characters")
        ]
    )
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """User registration form with admin approval workflow."""
    username = StringField(
        'Username', 
        validators=[
            DataRequired(message="Username is required"),
            Length(min=3, max=50, message="Username must be 3-50 characters")
        ]
    )
    email = StringField(
        'Email', 
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Please enter a valid email address"),
            Length(max=100, message="Email must be less than 100 characters")
        ]
    )
    first_name = StringField(
        'First Name', 
        validators=[
            DataRequired(message="First name is required"),
            Length(min=1, max=50, message="First name must be 1-50 characters")
        ]
    )
    last_name = StringField(
        'Last Name', 
        validators=[
            DataRequired(message="Last name is required"),
            Length(min=1, max=50, message="Last name must be 1-50 characters")
        ]
    )
    password = PasswordField(
        'Password', 
        validators=[
            DataRequired(message="Password is required"),
            Length(min=6, message="Password must be at least 6 characters")
        ]
    )
    password_confirm = PasswordField(
        'Confirm Password', 
        validators=[
            DataRequired(message="Please confirm your password"),
            EqualTo('password', message="Passwords must match")
        ]
    )
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Check if username is already taken."""
        user = User.query.filter_by(username=username.data.lower()).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different username.')

    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')
