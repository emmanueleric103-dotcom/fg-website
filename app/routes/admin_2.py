from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, current_app, flash
from app.extensions import db
from app.models import Admin, Service, Project, ContactMessage, SiteSetting, PageView, Visitor, DailyStat
from app.utils.helpers import admin_required, rate_limit_login, get_client_ip, slugify, generate_csrf_token, validate_csrf, get_site_setting
from app.utils.analytics import get_overview_stats, get_analytics_range, aggregate_daily_stats
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('is_admin'):
        return redirect(url_for('admin.dashboard'))
    
    error = None
    if request.method == 'POST':
        ip = get_client_ip()
        if not rate_limit_login(ip):
            error = "Too many login attempts. Try again in 5 minutes."
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.check_password(password):
                session['is_admin'] = True
                session['admin_id'] = admin.id
                session['admin_username'] = admin.username
                session.permanent = True
                admin.last_login = datetime.now(timezone.utc)
                db.session.commit()
                next_url = request.args.get('next') or url_for('admin.dashboard')
                return redirect(next_url)
            else:
                error = "Invalid username or password"
    
    return render_template('admin/login.html', error=error)

@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@admin_required
def dashboard():
    stats = get_overview_stats()
    return render_template('admin/dashboard.html', stats=stats, csrf_token=generate_csrf_token())

@admin_bp.route('/analytics')
@admin_required
def analytics():
    days = request.args.get('days', '7')
    try:
        days_int = int(days)
        if days_int not in [7,30,90]:
            days_int = 7
    except:
        days_int = 7
    
    data = get_analytics_range(days_int)
    return render_template('admin/analytics.html', data=data, days=days_int, csrf_token=generate_csrf_token())

@admin_bp.route('/services')
@admin_required
def services_list():
    services = Service.query.order_by(Service.order_index, Service.id).all()
    return render_template('admin/services.html', services=services, csrf_token=generate_csrf_token())

@admin_bp.route('/services/new', methods=['GET','POST'])
@admin_required
def service_new():
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            return "Invalid CSRF", 400
        title = request.form.get('title','').strip()
        description = request.form.get('description','').strip()
        short_desc = request.form.get('short_description','').strip()
        icon = request.form.get('icon','code').strip()
        is_published = request.form.get('is_published') == 'on'
        order_index = int(request.form.get('order_index', 0) or 0)
        
        if not title or not description:
            flash("Title and description required")
            return render_template('admin/service_form.html', csrf_token=generate_csrf_token(), service=None)
        
        slug = slugify(title)
        # ensure unique
        base_slug = slug
        counter = 1
        while Service.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter+=1
        
        s = Service(
            title=title,
            slug=slug,
            description=description,
            short_description=short_desc,
            icon=icon,
            is_published=is_published,
            order_index=order_index
        )
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('admin.services_list'))
    
    return render_template('admin/service_form.html', csrf_token=generate_csrf_token(), service=None)

@admin_bp.route('/services/<int:id>/edit', methods=['GET','POST'])
@admin_required
def service_edit(id):
    service = Service.query.get_or_404(id)
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            return "Invalid CSRF", 400
        service.title = request.form.get('title','').strip()
        service.description = request.form.get('description','').strip()
        service.short_description = request.form.get('short_description','').strip()
        service.icon = request.form.get('icon','code').strip()
        service.is_published = request.form.get('is_published') == 'on'
        service.order_index = int(request.form.get('order_index', 0) or 0)
        # Keep slug same unless title changed significantly? Keep for simplicity
        new_slug = slugify(service.title)
        if new_slug != service.slug:
            # check unique
            if not Service.query.filter(Service.slug==new_slug, Service.id!=service.id).first():
                service.slug = new_slug
        db.session.commit()
        return redirect(url_for('admin.services_list'))
    return render_template('admin/service_form.html', csrf_token=generate_csrf_token(), service=service)

@admin_bp.route('/services/<int:id>/delete', methods=['POST'])
@admin_required
def service_delete(id):
    token = request.form.get('csrf_token')
    if not validate_csrf(token):
        return jsonify({'error':'Invalid CSRF'}), 400
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('admin.services_list'))

@admin_bp.route('/projects')
@admin_required
def projects_list():
    projects = Project.query.order_by(Project.order_index, Project.id.desc()).all()
    return render_template('admin/projects.html', projects=projects, csrf_token=generate_csrf_token())

@admin_bp.route('/projects/new', methods=['GET','POST'])
@admin_required
def project_new():
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            return "Invalid CSRF", 400
        title = request.form.get('title','').strip()
        description = request.form.get('description','').strip()
        short_desc = request.form.get('short_description','').strip()
        image_url = request.form.get('image_url','').strip()
        technologies = request.form.get('technologies','').strip()
        category = request.form.get('category','').strip()
        live_url = request.form.get('live_url','').strip()
        source_url = request.form.get('source_url','').strip()
        is_featured = request.form.get('is_featured') == 'on'
        is_published = request.form.get('is_published') == 'on'
        order_index = int(request.form.get('order_index',0) or 0)
        
        if not title or not description:
            flash("Title and description required")
            return render_template('admin/project_form.html', csrf_token=generate_csrf_token(), project=None)
        
        slug = slugify(title)
        base_slug = slug
        counter=1
        while Project.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter+=1
        
        p = Project(
            title=title,
            slug=slug,
            description=description,
            short_description=short_desc,
            image_url=image_url,
            technologies=technologies,
            category=category,
            live_url=live_url,
            source_url=source_url,
            is_featured=is_featured,
            is_published=is_published,
            order_index=order_index
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('admin.projects_list'))
    return render_template('admin/project_form.html', csrf_token=generate_csrf_token(), project=None)

@admin_bp.route('/projects/<int:id>/edit', methods=['GET','POST'])
@admin_required
def project_edit(id):
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            return "Invalid CSRF", 400
        project.title = request.form.get('title','').strip()
        project.description = request.form.get('description','').strip()
        project.short_description = request.form.get('short_description','').strip()
        project.image_url = request.form.get('image_url','').strip()
        project.technologies = request.form.get('technologies','').strip()
        project.category = request.form.get('category','').strip()
        project.live_url = request.form.get('live_url','').strip()
        project.source_url = request.form.get('source_url','').strip()
        project.is_featured = request.form.get('is_featured') == 'on'
        project.is_published = request.form.get('is_published') == 'on'
        project.order_index = int(request.form.get('order_index',0) or 0)
        new_slug = slugify(project.title)
        if new_slug != project.slug and not Project.query.filter(Project.slug==new_slug, Project.id!=project.id).first():
            project.slug = new_slug
        db.session.commit()
        return redirect(url_for('admin.projects_list'))
    return render_template('admin/project_form.html', csrf_token=generate_csrf_token(), project=project)

@admin_bp.route('/projects/<int:id>/delete', methods=['POST'])
@admin_required
def project_delete(id):
    token = request.form.get('csrf_token')
    if not validate_csrf(token):
        return jsonify({'error':'Invalid CSRF'}), 400
    proj = Project.query.get_or_404(id)
    db.session.delete(proj)
    db.session.commit()
    return redirect(url_for('admin.projects_list'))

@admin_bp.route('/contacts')
@admin_required
def contacts():
    status = request.args.get('status')
    q = ContactMessage.query
    if status and status in ['new','read','resolved']:
        q = q.filter_by(status=status)
    search = request.args.get('search','').strip()
    if search:
        q = q.filter(
            (ContactMessage.name.ilike(f'%{search}%')) |
            (ContactMessage.email.ilike(f'%{search}%')) |
            (ContactMessage.message.ilike(f'%{search}%'))
        )
    messages = q.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/contacts.html', messages=messages, status=status, search=search, csrf_token=generate_csrf_token())

@admin_bp.route('/contacts/<int:id>/status', methods=['POST'])
@admin_required
def contact_status(id):
    token = request.form.get('csrf_token') or request.json.get('csrf_token') if request.is_json else None
    # For simplicity accept form
    if request.form:
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            return jsonify({'error':'Invalid CSRF'}), 400
        new_status = request.form.get('status')
    else:
        data = request.get_json() or {}
        token = data.get('csrf_token')
        if not validate_csrf(token):
            return jsonify({'error':'Invalid CSRF'}), 400
        new_status = data.get('status')
    
    if new_status not in ['new','read','resolved']:
        return jsonify({'error':'Invalid status'}), 400
    msg = ContactMessage.query.get_or_404(id)
    msg.status = new_status
    db.session.commit()
    if request.is_json:
        return jsonify({'ok': True})
    return redirect(url_for('admin.contacts'))

@admin_bp.route('/contacts/<int:id>/delete', methods=['POST'])
@admin_required
def contact_delete(id):
    token = request.form.get('csrf_token')
    if not validate_csrf(token):
        return jsonify({'error':'Invalid CSRF'}), 400
    msg = ContactMessage.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    return redirect(url_for('admin.contacts'))

@admin_bp.route('/settings', methods=['GET','POST'])
@admin_required
def settings():
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if not validate_csrf(token):
            return "Invalid CSRF", 400
        # Save all settings
        keys = [
            'brand_name','brand_tagline','brand_description','about_content',
            'contact_email','contact_phone','whatsapp_number','telegram_url',
            'github_url','twitter_url','linkedin_url','instagram_url',
            'seo_title','seo_description','homepage_headline','homepage_subheadline',
            'privacy_notice','timezone','analytics_retention_days'
        ]
        for k in keys:
            v = request.form.get(k,'').strip()
            SiteSetting.set(k, v)
        db.session.commit()
        flash("Settings saved")
        return redirect(url_for('admin.settings'))
    
    # GET
    settings_dict = {}
    for s in SiteSetting.query.all():
        settings_dict[s.key] = s.value
    # defaults for form
    defaults = {
        'brand_name': 'FG (HefGe)',
        'brand_tagline': 'I Build Digital Solutions That Work.',
        'brand_description': 'I build bots, websites, automation tools, and digital products that solve real problems.',
        'about_content': 'I am FG (HefGe) — a developer passionate about building digital solutions that work.',
        'contact_email': '',
        'contact_phone': '',
        'whatsapp_number': '',
        'telegram_url': '',
        'github_url': '',
        'twitter_url': '',
        'linkedin_url': '',
        'instagram_url': '',
        'seo_title': 'FG (HefGe) - Digital Solutions Developer',
        'seo_description': 'FG (HefGe) builds bots, websites, automation tools and digital products.',
        'homepage_headline': 'I Build Digital Solutions That Work.',
        'homepage_subheadline': 'I build bots, websites, automation tools, and digital products that solve real problems.',
        'privacy_notice': 'This site uses privacy-conscious analytics.',
        'timezone': 'Africa/Lagos',
        'analytics_retention_days': '90'
    }
    for k,v in defaults.items():
        if k not in settings_dict:
            settings_dict[k]=v
    return render_template('admin/settings.html', settings=settings_dict, csrf_token=generate_csrf_token())

@admin_bp.route('/settings/password', methods=['POST'])
@admin_required
def change_password():
    token = request.form.get('csrf_token')
    if not validate_csrf(token):
        return "Invalid CSRF", 400
    current_pw = request.form.get('current_password','')
    new_pw = request.form.get('new_password','')
    confirm_pw = request.form.get('confirm_password','')
    
    admin = Admin.query.get(session.get('admin_id'))
    if not admin or not admin.check_password(current_pw):
        flash("Current password incorrect", "error")
        return redirect(url_for('admin.settings'))
    if len(new_pw) < 8:
        flash("New password must be at least 8 characters", "error")
        return redirect(url_for('admin.settings'))
    if new_pw != confirm_pw:
        flash("Passwords do not match", "error")
        return redirect(url_for('admin.settings'))
    
    admin.set_password(new_pw)
    db.session.commit()
    flash("Password changed successfully", "success")
    return redirect(url_for('admin.settings'))

@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    days = request.args.get('days', '7')
    try:
        days_int = int(days)
    except:
        days_int = 7
    data = get_analytics_range(days_int)
    return jsonify(data)

@admin_bp.route('/api/aggregate', methods=['POST'])
@admin_required
def api_aggregate():
    token = request.json.get('csrf_token') if request.is_json else request.form.get('csrf_token')
    if not validate_csrf(token):
        return jsonify({'error':'Invalid CSRF'}), 400
    # Aggregate today
    from datetime import date
    aggregate_daily_stats()
    return jsonify({'ok': True})
