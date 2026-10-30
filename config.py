import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'botpilot-perfect-secret-2024')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///botpilot.db')
    # Render gives postgres:// fix it
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Resend
    RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'onboarding@resend.dev')
    FROM_NAME = os.getenv('FROM_NAME', 'BotPilot')
    
    # Auth
    CODE_EXPIRY_MINUTES = 10
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
