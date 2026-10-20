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
            from app.models import Service as ServiceModel
            if ServiceModel.query.count() == 0:
                default_services = [
                    {"title": "Telegram Bot Development", "description": "Custom Telegram shop bots, utility bots, automated workflows, and API integrations.", "short_description": "Shop bots, utility bots, custom automation", "icon": "bot", "order_index": 1},
                    {"title": "Free Fire Sensitivity Solutions", "description": "Personalized sensitivity settings, custom configs, and gaming tools.", "short_description": "Custom sensitivity & gaming tools", "icon": "gamepad-2", "order_index": 2},
                    {"title": "Website Development", "description": "Modern, fast, responsive websites.", "short_description": "Portfolios, business sites, web apps", "icon": "globe", "order_index": 3},
                    {"title": "【entity-Shopify¦canonical_name=Shopify】 Store Setup", "description": "Complete 【entity-Shopify¦canonical_name=Shopify】 store configuration.", "short_description": "Store setup, design & integrations", "icon": "shopping-bag", "order_index": 4},
                    {"title": "Trading Automation", "description": "Trading scanners, alerts, Telegram integrations. No guaranteed profits.", "short_description": "Scanners, alerts & bot development", "icon": "trending-up", "order_index": 5},
                    {"title": "Python and Termux Projects", "description": "Custom Python scripts and mobile-based development.", "short_description": "Scripts, automation & mobile dev", "icon": "terminal", "order_index": 6},
                    {"title": "Digital Products", "description": "E-books, strategy notes, software tools.", "short_description": "E-books, tools & resources", "icon": "package", "order_index": 7},
                    {"title": "Custom Projects", "description": "Describe your idea and request a quote.", "short_description": "Bring your idea, get a quote", "icon": "lightbulb", "order_index": 8},
                ]
                for svc in default_services:
                    from app.utils.helpers import slugify
                    s = ServiceModel(title=svc['title'], slug=slugify(svc['title']), description=svc['description'], short_description=svc['short_description'], icon=svc['icon'], order_index=svc['order_index'], is_published=True)
                    db.session.add(s)
                print("Default services created")
            admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_pass = os.environ.get('ADMIN_PASSWORD')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            if not Admin.query.filter_by(username=admin_user).first():
                if admin_pass:
                    admin = Admin(username=admin_user, email=admin_email)
                    admin.set_password(admin_pass)
                    db.session.add(admin)
                    print(f"Admin user '{admin_user}' created")
                else:
                    print("ADMIN_PASSWORD not set")
            else:
                print(f"Admin '{admin_user}' already exists")
            defaults = {'brand_name': 'FG (HefGe)', 'timezone': app.config.get('TIMEZONE', 'Africa/Lagos')}
            for k,v in defaults.items():
                if not SiteSetting.query.filter_by(key=k).first():
                    SiteSetting.set(k, v)
            db.session.commit()
            print("Database initialized")
    return app
