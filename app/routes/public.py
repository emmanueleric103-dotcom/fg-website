from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response, current_app, abort
from app.extensions import db
from app.models import Service, Project, ContactMessage, SiteSetting, PageView, Visitor
from app.utils.helpers import get_visitor_id, is_admin_request, get_client_ip, slugify
from datetime import datetime, timezone, timedelta
import json

public_bp = Blueprint('public', __name__)

def get_settings_dict():
    settings = {}
    all_settings = SiteSetting.query.all()
    for s in all_settings:
        settings[s.key] = s.value
    # Defaults
    defaults = {
        'brand_name': 'FG (HefGe)',
        'brand_tagline': 'I Build Digital Solutions That Work.',
        'brand_description': 'I build bots, websites, automation tools, and digital products that solve real problems. Focused on clean code, smart automation, and results that matter.',
        'about_content': 'I am FG (HefGe) — a developer passionate about building digital solutions that work. I specialize in Telegram bots, website development, trading automation, and Python tools. My approach is simple: understand the problem, build a clean solution, and make it work reliably.',
        'contact_email': '',
        'contact_phone': '',
        'whatsapp_number': '',
        'telegram_url': '',
        'github_url': '',
        'twitter_url': '',
        'linkedin_url': '',
        'instagram_url': '',
        'seo_title': 'FG (HefGe) - Digital Solutions Developer',
        'seo_description': 'FG (HefGe) builds bots, websites, automation tools and digital products. Telegram bots, Free Fire tools, Shopify stores, trading automation and more.',
        'homepage_headline': 'I Build Digital Solutions That Work.',
        'homepage_subheadline': 'I build bots, websites, automation tools, and digital products that solve real problems. Clean code, smart automation, reliable results.',
        'privacy_notice': 'This site uses privacy-conscious analytics to understand visitor trends. We use a random first-party identifier, not personal data. No precise location or message contents are collected.',
        'timezone': 'Africa/Lagos'
    }
    for k, v in defaults.items():
        if k not in settings or not settings[k]:
            settings[k] = v
    return settings

@public_bp.before_app_request
def track_visitor():
    # Exclude admin, static, api, sitemap
    if request.path.startswith('/static/') or request.path.startswith('/admin') or request.path.startswith('/api/track'):
        return
    if request.path in ['/robots.txt', '/sitemap.xml', '/favicon.ico']:
        return
    # Exclude if admin session
    from flask import session
    if session.get('is_admin'):
        return
    
    # Get visitor ID
    visitor_id = request.cookies.get('fg_visitor_id')
    is_new_visitor_cookie = False
    if not visitor_id:
        import uuid
        visitor_id = str(uuid.uuid4())
        is_new_visitor_cookie = True
    
    # Throttle duplicate: same visitor + same path within 30 seconds
    try:
        recent = PageView.query.filter(
            PageView.visitor_id == visitor_id,
            PageView.page_path == request.path,
            PageView.timestamp >= datetime.now(timezone.utc) - timedelta(seconds=30)
        ).first()
        if recent:
            # Still set cookie if needed but don't count
            if is_new_visitor_cookie:
                # Need to set cookie later via after_request, store in g
                from flask import g
                g.new_visitor_id = visitor_id
            return
    except:
        pass
    
    # Record visitor if new
    try:
        existing_visitor = Visitor.query.filter_by(visitor_id=visitor_id).first()
        if not existing_visitor:
            v = Visitor(
                visitor_id=visitor_id,
                user_agent=request.headers.get('User-Agent', '')[:500],
                referrer=request.headers.get('Referer', '')[:500],
                landing_page=request.path[:500]
            )
            db.session.add(v)
        else:
            existing_visitor.last_seen = datetime.now(timezone.utc)
        
        pv = PageView(
            visitor_id=visitor_id,
            page_path=request.path[:500],
            page_title=request.path,
            user_agent=request.headers.get('User-Agent', '')[:500],
            referrer=request.headers.get('Referer', '')[:500],
            is_admin=False
        )
        db.session.add(pv)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Analytics error: {e}")
    
    # Store for after_request cookie setting
    if is_new_visitor_cookie:
        from flask import g
        g.new_visitor_id = visitor_id

@public_bp.after_app_request
def set_visitor_cookie(response):
    from flask import g
    if hasattr(g, 'new_visitor_id'):
        # 1 year
        response.set_cookie('fg_visitor_id', g.new_visitor_id, max_age=31536000, httponly=True, samesite='Lax')
    return response

@public_bp.route('/')
def index():
    settings = get_settings_dict()
    featured_services = Service.query.filter_by(is_published=True).order_by(Service.order_index, Service.id).limit(6).all()
    featured_projects = Project.query.filter_by(is_published=True, is_featured=True).order_by(Project.order_index).limit(6).all()
    if not featured_projects:
        featured_projects = Project.query.filter_by(is_published=True).order_by(Project.order_index).limit(3).all()
    return render_template('index.html', settings=settings, services=featured_services, projects=featured_projects)

@public_bp.route('/services')
def services():
    settings = get_settings_dict()
    all_services = Service.query.filter_by(is_published=True).order_by(Service.order_index, Service.id).all()
    return render_template('services.html', settings=settings, services=all_services)

@public_bp.route('/services/<slug>')
def service_detail(slug):
    settings = get_settings_dict()
    service = Service.query.filter_by(slug=slug, is_published=True).first_or_404()
    # Increment view count (simple)
    service.views = (service.views or 0) + 1
    db.session.commit()
    return render_template('service_detail.html', settings=settings, service=service)

@public_bp.route('/projects')
def projects():
    settings = get_settings_dict()
    category = request.args.get('category')
    q = Project.query.filter_by(is_published=True)
    if category:
        q = q.filter_by(category=category)
    all_projects = q.order_by(Project.order_index, Project.created_at.desc()).all()
    categories = db.session.query(Project.category).filter(Project.is_published==True).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    return render_template('projects.html', settings=settings, projects=all_projects, categories=categories, active_category=category)

@public_bp.route('/projects/<slug>')
def project_detail(slug):
    settings = get_settings_dict()
    project = Project.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('project_detail.html', settings=settings, project=project)

@public_bp.route('/about')
def about():
    settings = get_settings_dict()
    return render_template('about.html', settings=settings)

@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    settings = get_settings_dict()
    services_list = Service.query.filter_by(is_published=True).order_by(Service.order_index).all()
    
    if request.method == 'POST':
        # Honeypot
        if request.form.get('website'):
            return render_template('contact.html', settings=settings, services=services_list, error="Spam detected")
        
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        service_interest = request.form.get('service_interest', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validation
        errors = []
        if not name or len(name) < 2:
            errors.append("Name must be at least 2 characters")
        if not email or '@' not in email:
            errors.append("Valid email required")
        if not message or len(message) < 10:
            errors.append("Message must be at least 10 characters")
        if len(message) > 5000:
            errors.append("Message too long (max 5000 chars)")
        
        if errors:
            return render_template('contact.html', settings=settings, services=services_list, errors=errors, form_data=request.form)
        
        # Save
        try:
            cm = ContactMessage(
                name=name[:200],
                email=email[:200],
                service_interest=service_interest[:200],
                message=message[:5000],
                ip_address=get_client_ip()
            )
            db.session.add(cm)
            db.session.commit()
            return render_template('contact.html', settings=settings, services=services_list, success=True)
        except Exception as e:
            db.session.rollback()
            return render_template('contact.html', settings=settings, services=services_list, error="Failed to send message. Please try again.")
    
    return render_template('contact.html', settings=settings, services=services_list)

@public_bp.route('/privacy')
def privacy():
    settings = get_settings_dict()
    return render_template('privacy.html', settings=settings)

@public_bp.route('/robots.txt')
def robots():
    site_url = current_app.config.get('SITE_URL', '')
    content = f"User-agent: *\nAllow: /\n\nSitemap: {site_url}/sitemap.xml\n"
    return current_app.response_class(content, mimetype='text/plain')

@public_bp.route('/sitemap.xml')
def sitemap():
    settings = get_settings_dict()
    site_url = current_app.config.get('SITE_URL', 'http://localhost:5000').rstrip('/')
    
    pages = [
        {'loc': f"{site_url}/", 'priority': '1.0'},
        {'loc': f"{site_url}/services", 'priority': '0.9'},
        {'loc': f"{site_url}/projects", 'priority': '0.9'},
        {'loc': f"{site_url}/about", 'priority': '0.7'},
        {'loc': f"{site_url}/contact", 'priority': '0.8'},
        {'loc': f"{site_url}/privacy", 'priority': '0.3'},
    ]
    services = Service.query.filter_by(is_published=True).all()
    for s in services:
        pages.append({'loc': f"{site_url}/services/{s.slug}", 'priority': '0.8'})
    
    projects = Project.query.filter_by(is_published=True).all()
    for p in projects:
        pages.append({'loc': f"{site_url}/projects/{p.slug}", 'priority': '0.7'})
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for pg in pages:
        xml.append(f"  <url><loc>{pg['loc']}</loc><priority>{pg['priority']}</priority></url>")
    xml.append('</urlset>')
    return current_app.response_class('\n'.join(xml), mimetype='application/xml')

@public_bp.route('/api/track', methods=['POST'])
def api_track():
    # Optional JS-enhanced tracking - same logic but from JS
    # Already handled by before_request, this is just for extra data
    return jsonify({'ok': True})
