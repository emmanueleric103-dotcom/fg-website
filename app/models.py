from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(300))
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(10))
    code_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # For saving sensi
    sensitivities = db.relationship('Sensitivity', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_code(self):
        code = str(secrets.randbelow(900000) + 100000)  # 6 digits
        self.verification_code = code
        self.code_expiry = datetime.utcnow() + timedelta(minutes=10)
        return code

class Sensitivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    game_type = db.Column(db.String(20))  # FF or COD
    device_model = db.Column(db.String(100))
    config_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SensitivityReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensitivity_id = db.Column(db.Integer, db.ForeignKey('sensitivity.id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
