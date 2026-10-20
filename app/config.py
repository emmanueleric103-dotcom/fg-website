import os
from datetime import timedelta

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production-please-32chars-min'
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
        elif database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        db_path = os.path.join(BASE_DIR, 'instance', 'fg_website.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    SITE_URL = os.environ.get('SITE_URL', 'http://localhost:5000').rstrip('/')
    TIMEZONE = os.environ.get('TIMEZONE', 'Africa/Lagos')
    ANALYTICS_RETENTION_DAYS = int(os.environ.get('ANALYTICS_RETENTION_DAYS', '90'))
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@fghefge.com')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    LOGIN_RATE_LIMIT = 5
    LOGIN_RATE_WINDOW = 300
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_ENABLED = True

class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True

class DevelopmentConfig(Config):
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = False

config_by_name = {'production': ProductionConfig, 'development': DevelopmentConfig, 'default': DevelopmentConfig}
