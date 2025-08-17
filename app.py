import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from config import config

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

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
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login (will be defined in models)
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(user_id)
    
    # Register blueprints (routes)
    from routes.auth import auth_bp
    from routes.events import events_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    
    # Database tables will be created in Chunk 1B with proper models
    # with app.app_context():
    #     db.create_all()
    
    return app

# Create app instance for development
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
