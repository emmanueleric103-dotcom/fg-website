from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.tools import tools_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tools_bp, url_prefix='/tools')
    
    with app.app_context():
        # Auto create tables - fixes 500 error
        try:
            from app import models
            db.create_all()
            print("AUTO-SEED OK - All tables created including User, SensitivityReview")
        except Exception as e:
            print(f"DB create error: {e}")
    
    return app
