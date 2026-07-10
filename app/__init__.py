from flask import Flask
from flask_login import LoginManager
from app.config import Config
from app.models import db

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.workouts import workouts_bp
    from app.routes.exercises import exercises_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(workouts_bp, url_prefix='/workouts')
    app.register_blueprint(exercises_bp, url_prefix='/exercises')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Add custom jinja filter or context processors if needed (e.g. for theme)
    @app.context_processor
    def inject_preferences():
        from flask_login import current_user
        from app.models.progress import UserPreference
        
        dark_mode = True # Default
        if current_user.is_authenticated:
            pref = UserPreference.query.filter_by(user_id=current_user.id).first()
            if pref:
                dark_mode = pref.dark_mode
        return dict(dark_mode=dark_mode)

    return app
