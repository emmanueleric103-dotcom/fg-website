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
    
    # Init extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from app.routes.public import get_settings_dict
        try:
            settings = get_settings_dict()
        except:
            settings = {'brand_name': 'FG (HefGe)'}
        return app.jinja_env.get_template('404.html').render(settings=settings), 404
    
    @app.errorhandler(500)
    def server_error(e):
        from app.routes.public import get_settings_dict
        try:
            settings = get_settings_dict()
        except:
            settings = {'brand_name': 'FG (HefGe)'}
        return app.jinja_env.get_template('500.html').render(settings=settings), 500
    
    # Context processor for settings
    @app.context_processor
    def inject_settings():
        try:
            from app.routes.public import get_settings_dict
            return {'site_settings': get_settings_dict()}
        except:
            return {'site_settings': {}}
    
    # CLI command to init db and admin
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize database and create default admin"""
        with app.app_context():
            db.create_all()
            # Create default services if none
            if Service.query.count() == 0:
                from app.models import Service
                default_services = [
                    {"title": "Telegram Bot Development", "description": "Custom Telegram shop bots, utility bots, automated workflows, and API integrations. I build reliable bots that handle payments, orders, and customer support automatically.", "short_description": "Shop bots, utility bots, custom automation", "icon": "bot", "order_index": 1},
                    {"title": "Free Fire Sensitivity Solutions", "description": "Personalized sensitivity settings, custom configs, and gaming tools to improve your Free Fire gameplay. Optimized for different devices and playstyles.", "short_description": "Custom sensitivity & gaming tools", "icon": "gamepad-2", "order_index": 2},
                    {"title": "Website Development", "description": "Modern, fast, responsive websites - from personal portfolios and business sites to landing pages and full web applications. Built with clean code and optimized for performance.", "short_description": "Portfolios, business sites, web apps", "icon": "globe", "order_index": 3},
                    {"title": "Shopify Store Setup", "description": "Complete Shopify store configuration: product setup, theme customization, payment integration, and automation. Get your store ready to sell fast.", "short_description": "Store setup, design & integrations", "icon": "shopping-bag", "order_index": 4},
                    {"title": "Trading Automation", "description": "Trading scanners, real-time alerts, Telegram integrations, and custom trading bot development. Automate your analysis, not your financial decisions. No guaranteed profits.", "short_description": "Scanners, alerts & bot development", "icon": "trending-up", "order_index": 5},
                    {"title": "Python and Termux Projects", "description": "Custom Python scripts, automation tools, and mobile-based development projects running directly on Android via Termux. Automation that works anywhere.", "short_description": "Scripts, automation & mobile dev", "icon": "terminal", "order_index": 6},
                    {"title": "Digital Products", "description": "E-books, strategy notes, software tools, templates and other digital resources to help you build faster and smarter.", "short_description": "E-books, tools & resources", "icon": "package", "order_index": 7},
                    {"title": "Custom Projects", "description": "Have an idea that doesn't fit the boxes? Describe your project and let's build it. Custom solutions tailored to your specific needs.", "short_description": "Bring your idea, get a quote", "icon": "lightbulb", "order_index": 8},
                ]
                for svc in default_services:
                    from app.utils.helpers import slugify
                    s = Service(
                        title=svc['title'],
                        slug=slugify(svc['title']),
                        description=svc['description'],
                        short_description=svc['short_description'],
                        icon=svc['icon'],
                        order_index=svc['order_index'],
                        is_published=True
                    )
                    db.session.add(s)
                print("Default services created")
            
            # Create admin
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
                    print("ADMIN_PASSWORD not set - admin not created. Set env vars and run again.")
            else:
                print(f"Admin '{admin_user}' already exists")
            
            # Default site settings
            defaults = {
                'brand_name': 'FG (HefGe)',
                'timezone': app.config.get('TIMEZONE', 'Africa/Lagos')
            }
            for k,v in defaults.items():
                if not SiteSetting.query.filter_by(key=k).first():
                    SiteSetting.set(k, v)
            
            db.session.commit()
            print("Database initialized")
    
    return app
