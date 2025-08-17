import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with common settings."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email settings (abstract for flexibility)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@arlingtonmenscircle.com'
    
    # AWS Settings (for future use)
    AWS_REGION = os.environ.get('AWS_REGION') or 'us-east-1'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    # Application settings
    AMC_ADMIN_EMAIL = os.environ.get('AMC_ADMIN_EMAIL') or 'admin@arlingtonmenscircle.com'
    AMC_GROUP_NAME = 'Arlington Men\'s Circle'

class DevelopmentConfig(Config):
    """Development configuration - SQLite, console email."""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'amc_website_dev.db')
    
    # Email to console for development
    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = True

class ProductionConfig(Config):
    """Production configuration - PostgreSQL, SES email."""
    
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'amc_website.db')
    
    # Production email settings (SES)
    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = False

class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True

# Configuration dictionary for easy switching
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
