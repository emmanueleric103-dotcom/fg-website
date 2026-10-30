from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.utils.email_sender import send_verification_email
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        
        if not email or not password:
            flash('Email and password required', 'error')
            return render_template('auth/register.html')
        
        existing = User.query.filter_by(email=email).first()
        if existing:
            if existing.is_verified:
                flash('Email already registered. Please login.', 'error')
                return redirect(url_for('auth.login'))
            # resend code for unverified
            code = existing.generate_code()
            existing.set_password(password)
            db.session.commit()
            sent, debug_info = send_verification_email(email, code)
            flash(f'Code sent to {email}. {debug_info}', 'info')
            return redirect(url_for('auth.verify', email=email))
        
        user = User(email=email)
        user.set_password(password)
        code = user.generate_code()
        db.session.add(user)
        db.session.commit()
        
        sent, debug_info = send_verification_email(email, code)
        
        if sent:
            flash(f'Verification code sent to {email}', 'success')
        else:
            # Still allow testing - show in logs + popup
            flash(f'{debug_info} - Check Render Logs for code', 'info')
        
        return redirect(url_for('auth.verify', email=email))
    
    return render_template('auth/register.html')

@auth_bp.route('/verify', methods=['GET', 'POST'])
def verify():
    email = request.args.get('email') or request.form.get('email','')
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        code = request.form.get('code','').strip()
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found', 'error')
            return render_template('auth/verify.html', email=email)
        
        if user.code_expiry and datetime.utcnow() > user.code_expiry:
            flash('Code expired. New code sent.', 'error')
            new_code = user.generate_code()
            db.session.commit()
            send_verification_email(email, new_code)
            return render_template('auth/verify.html', email=email)
        
        if user.verification_code == code:
            user.is_verified = True
            user.verification_code = None
            db.session.commit()
            login_user(user)
            flash('Email verified! Welcome to BotPilot', 'success')
            return redirect(url_for('tools.sensitivity'))
        else:
            flash('Invalid code. Try again.', 'error')
    
    return render_template('auth/verify.html', email=email)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mode = request.form.get('mode', 'password')  # password or code
        email = request.form.get('email','').strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('No account with that email', 'error')
            return render_template('auth/login.html')
        
        if mode == 'code':
            # Send login code via Resend
            code = user.generate_code()
            db.session.commit()
            sent, debug_info = send_verification_email(email, code, login=True)
            flash(f'Login code sent. {debug_info}', 'info')
            return redirect(url_for('auth.verify', email=email))
        
        # password mode
        password = request.form.get('password','')
        if not user.check_password(password):
            flash('Wrong password', 'error')
            return render_template('auth/login.html')
        
        if not user.is_verified:
            code = user.generate_code()
            db.session.commit()
            send_verification_email(email, code)
            flash('Please verify your email first. Code resent.', 'info')
            return redirect(url_for('auth.verify', email=email))
        
        login_user(user)
        flash('Logged in!', 'success')
        return redirect(url_for('tools.sensitivity'))
    
    return render_template('auth/login.html')

@auth_bp.route('/resend-code', methods=['POST'])
def resend_code():
    email = request.json.get('email') or request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'ok': False, 'msg': 'User not found'})
    code = user.generate_code()
    db.session.commit()
    sent, debug = send_verification_email(email, code)
    return jsonify({'ok': True, 'msg': debug, 'sent': sent, 'code_for_debug': code if not sent else None})

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
