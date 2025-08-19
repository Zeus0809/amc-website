import os
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from config import config
from models import db, migrate, init_db, User

# Initialize Flask extensions (login and mail only - db handled in models)
login_manager = LoginManager()
mail = Mail()

def create_app(config_name=None):
    """Application factory pattern for flexible configuration."""
    
    # Get config name from environment or use default
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize database with all models
    init_db(app)
    
    # Initialize other extensions with app
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, user_id)
    
    # Register blueprints (routes)
    from routes.auth import auth_bp
    from routes.events import events_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    
    return app

# Create app instance for development
app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
