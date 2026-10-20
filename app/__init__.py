from flask import Flask
from app.config import config_by_name
from app.extensions import db
from app.routes.public import public_bp
from app.routes.admin import admin_bp
from app.models import SiteSetting, Admin, Service
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        if config_name == 'production':
            config_name = 'production'
        else:
            config_name = 'development'
    
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    
    db.init_app(app)
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    
    # AUTO-CREATE TABLES ON STARTUP - NO SHELL NEEDED
    with app.app_context():
        try:
            db.create_all()
            admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_pass = os.environ.get('ADMIN_PASSWORD')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            if admin_pass and not Admin.query.filter_by(username=admin_user).first():
                admin = Admin(username=admin_user, email=admin_email)
                admin.set_password(admin_pass)
                db.session.add(admin)
                db.session.commit()
                print(f"AUTO-CREATED admin '{admin_user}'")
            if Service.query.count() == 0:
                from app.utils.helpers import slugify
                default_services = [
                    {"title": "Telegram Bot Development", "description": "Custom Telegram shop bots.", "short_description": "Shop bots", "icon": "bot", "order_index": 1},
                    {"title": "Website Development", "description": "Modern websites.", "short_description": "Websites", "icon": "globe", "order_index": 2},
                    {"title": "【entity-Shopify¦canonical_name=Shopify】 Store Setup", "description": "【entity-Shopify¦canonical_name=Shopify】 stores.", "short_description": "【entity-Shopify¦canonical_name=Shopify】", "icon": "shopping-bag", "order_index": 3},
                ]
                for svc in default_services:
                    s = Service(title=svc['title'], slug=slugify(svc['title']), description=svc['description'], short_description=svc['short_description'], icon=svc['icon'], order_index=svc['order_index'], is_published=True)
                    db.session.add(s)
                db.session.commit()
            if not SiteSetting.query.filter_by(key='brand_name').first():
                SiteSetting.set('brand_name', 'FG (HefGe)')
        except Exception as e:
            print(f"Auto-init: {e}")

    @app.errorhandler(404)
    def not_found(e):
        from app.routes.public import get_settings_dict
        try: settings = get_settings_dict()
        except: settings = {'brand_name': 'FG (HefGe)'}
        return app.jinja_env.get_template('404.html').render(settings=settings), 404
    
    @app.errorhandler(500)
    def server_error(e):
        from app.routes.public import get_settings_dict
        try: settings = get_settings_dict()
        except: settings = {'brand_name': 'FG (HefGe)'}
        return app.jinja_env.get_template('500.html').render(settings=settings), 500
    
    @app.context_processor
    def inject_settings():
        try:
            from app.routes.public import get_settings_dict
            return {'site_settings': get_settings_dict()}
        except:
            return {'site_settings': {}}
    
    @app.cli.command('init-db')
    def init_db_command():
        with app.app_context():
            db.create_all()
            print("Database initialized")
    
    return app
