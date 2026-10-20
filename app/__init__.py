from flask import Flask
from app.config import config_by_name
from app.extensions import db
from app.routes.public import public_bp
from app.routes.admin import admin_bp
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
    with app.app_context():
        try:
            db.create_all()
            from app.models import Admin, Service, SiteSetting
            from app.utils.helpers import slugify
            au = os.environ.get('ADMIN_USERNAME', 'admin')
            ap = os.environ.get('ADMIN_PASSWORD')
            ae = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            if ap and not Admin.query.filter_by(username=au).first():
                a = Admin(username=au, email=ae)
                a.set_password(ap)
                db.session.add(a)
            if Service.query.count() == 0:
                services = [
                    {"title": "Telegram Bot Development", "desc": "Custom Telegram shop bots, utility bots, automated workflows, and API integrations. I build reliable bots that handle payments, orders, and customer support automatically.", "short": "Shop bots, utility bots, custom automation", "icon": "bot", "order": 1},
                    {"title": "Free Fire Sensitivity Solutions", "desc": "Personalized sensitivity settings, custom configs, and gaming tools to improve your Free Fire gameplay. Optimized for different devices and playstyles.", "short": "Custom sensitivity & gaming tools", "icon": "gamepad-2", "order": 2},
                    {"title": "Website Development", "desc": "Modern, fast, responsive websites - from personal portfolios and business sites to landing pages and full web applications. Built with clean code and optimized for performance.", "short": "Portfolios, business sites, web apps", "icon": "globe", "order": 3},
                    {"title": "Shopify Store Setup", "desc": "Complete Shopify store configuration: product setup, theme customization, payment integration, and automation. Get your store ready to sell fast.", "short": "Store setup, design & integrations", "icon": "shopping-bag", "order": 4},
                    {"title": "Trading Automation", "desc": "Trading scanners, real-time alerts, Telegram integrations, and custom trading bot development. Automate your analysis, not your financial decisions.", "short": "Scanners, alerts & bot development", "icon": "trending-up", "order": 5},
                    {"title": "Python and Termux Projects", "desc": "Custom Python scripts, automation tools, and mobile-based development projects running directly on Android via Termux.", "short": "Scripts, automation & mobile dev", "icon": "terminal", "order": 6},
                    {"title": "Digital Products", "desc": "E-books, strategy notes, software tools, templates and other digital resources to help you build faster and smarter.", "short": "E-books, tools & resources", "icon": "package", "order": 7},
                    {"title": "Custom Projects", "desc": "Have an idea that doesn't fit the boxes? Describe your project and let's build it. Custom solutions tailored to your specific needs.", "short": "Bring your idea, get a quote", "icon": "lightbulb", "order": 8},
                ]
                for svc in services:
                    s = Service(title=svc["title"], slug=slugify(svc["title"]), description=svc["desc"], short_description=svc["short"], icon=svc["icon"], order_index=svc["order"], is_published=True)
                    db.session.add(s)
            if not SiteSetting.query.filter_by(key='brand_name').first():
                SiteSetting.set('brand_name', 'FG (HefGe)')
                SiteSetting.set('timezone', 'Africa/Lagos')
            db.session.commit()
        except Exception as e:
            print(f"Auto-init: {e}")
    @app.errorhandler(404)
    def not_found(e):
        try:
            from app.routes.public import get_settings_dict
            s = get_settings_dict()
        except:
            s = {'brand_name': 'FG (HefGe)'}
        return app.jinja_env.get_template('404.html').render(settings=s), 404
    @app.errorhandler(500)
    def server_error(e):
        try:
            from app.routes.public import get_settings_dict
            s = get_settings_dict()
        except:
            s = {'brand_name': 'FG (HefGe)'}
        return app.jinja_env.get_template('500.html').render(settings=s), 500
    @app.context_processor
    def inject_settings():
        try:
            from app.routes.public import get_settings_dict
            return {'site_settings': get_settings_dict()}
        except:
            return {'site_settings': {}}
    return app
