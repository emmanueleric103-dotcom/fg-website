import uuid
import time
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, session, g, current_app
import hashlib
import json
from zoneinfo import ZoneInfo

# Simple in-memory rate limiter for login
_login_attempts = {}

def get_client_ip():
    # Respect X-Forwarded-For for Render/proxy
    xff = request.headers.get('X-Forwarded-For')
    if xff:
        return xff.split(',')[0].strip()
    return request.remote_addr or 'unknown'

def is_admin_request():
    return request.path.startswith('/admin') or session.get('is_admin')

def get_visitor_id():
    vid = request.cookies.get('fg_visitor_id')
    if not vid:
        vid = str(uuid.uuid4())
    return vid

def get_timezone():
    tz_name = current_app.config.get('TIMEZONE', 'Africa/Lagos')
    try:
        return ZoneInfo(tz_name)
    except:
        return ZoneInfo('Africa/Lagos')

def now_in_tz():
    tz = get_timezone()
    return datetime.now(tz)

def slugify(text):
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:200]

def rate_limit_login(ip):
    now = time.time()
    window = current_app.config.get('LOGIN_RATE_WINDOW', 300)
    limit = current_app.config.get('LOGIN_RATE_LIMIT', 5)
    
    # Clean old
    for key in list(_login_attempts.keys()):
        if now - _login_attempts[key]['first'] > window:
            del _login_attempts[key]
    
    rec = _login_attempts.get(ip)
    if not rec:
        _login_attempts[ip] = {'count': 1, 'first': now}
        return True
    if now - rec['first'] > window:
        _login_attempts[ip] = {'count': 1, 'first': now}
        return True
    if rec['count'] >= limit:
        return False
    rec['count'] += 1
    return True

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            from flask import redirect, url_for, request
            # For API, return 401
            if request.path.startswith('/admin/api') or request.accept_mimetypes.best == 'application/json':
                return {'error': 'Unauthorized'}, 401
            return redirect(url_for('admin.login', next=request.path))
        return f(*args, **kwargs)
    return decorated

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
    return session['csrf_token']

def validate_csrf(token):
    return token and session.get('csrf_token') and token == session.get('csrf_token')

def get_site_setting(key, default=''):
    from app.models import SiteSetting
    val = SiteSetting.get(key)
    return val if val is not None else default
