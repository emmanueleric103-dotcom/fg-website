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
            from app.models import Admin, SiteSetting
            au = os.environ.get('ADMIN_USERNAME', 'admin')
            ap = os.environ.get('ADMIN_PASSWORD')
            ae = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            if ap and not Admin.query.filter_by(username=au).first():
                a = Admin(username=au, email=ae)
                a.set_password(ap)
                db.session.add(a)
                db.session.commit()
            if not SiteSetting.query.filter_by(key='brand_name').first():
                SiteSetting.set('brand_name', 'FG (HefGe)')
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
