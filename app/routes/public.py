
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response, current_app, abort
from app.extensions import db
from app.models import Service, Project, ContactMessage, SiteSetting, PageView, Visitor, SensitivityReview
from app.utils.helpers import get_visitor_id, is_admin_request, get_client_ip, slugify
from datetime import datetime, timezone, timedelta
import json

public_bp = Blueprint('public', __name__)

def get_settings_dict():
    settings = {}
    all_settings = SiteSetting.query.all()
    for s in all_settings:
        settings[s.key] = s.value
    defaults = {
        'brand_name': 'FG (HefGe)',
        'brand_tagline': 'I Build Digital Solutions That Work.',
        'brand_description': 'I build bots, websites, automation tools, and digital products that solve real problems. Focused on clean code, smart automation, and results that matter.',
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
        'timezone': 'Africa/Lagos'
    }
    for k, v in defaults.items():
        if k not in settings or not settings[k]:
            settings[k] = v
    return settings

@public_bp.before_app_request
def track_visitor():
    if request.path.startswith('/static/') or request.path.startswith('/admin') or request.path.startswith('/api/track') or request.path.startswith('/api/sensitivity'):
        return
    if request.path in ['/robots.txt', '/sitemap.xml', '/favicon.ico']:
        return
    from flask import session
    if session.get('is_admin'):
        return
    visitor_id = request.cookies.get('fg_visitor_id')
    is_new_visitor_cookie = False
    if not visitor_id:
        import uuid
        visitor_id = str(uuid.uuid4())
        is_new_visitor_cookie = True
    try:
        recent = PageView.query.filter(
            PageView.visitor_id == visitor_id,
            PageView.page_path == request.path,
            PageView.timestamp >= datetime.now(timezone.utc) - timedelta(seconds=30)
        ).first()
        if recent:
            if is_new_visitor_cookie:
                from flask import g
                g.new_visitor_id = visitor_id
            return
    except:
        pass
    try:
        existing_visitor = Visitor.query.filter_by(visitor_id=visitor_id).first()
        if not existing_visitor:
            v = Visitor(visitor_id=visitor_id, user_agent=request.headers.get('User-Agent','')[:500], referrer=request.headers.get('Referer','')[:500], landing_page=request.path[:500])
            db.session.add(v)
        else:
            existing_visitor.last_seen = datetime.now(timezone.utc)
        pv = PageView(visitor_id=visitor_id, page_path=request.path[:500], page_title=request.path, user_agent=request.headers.get('User-Agent','')[:500], referrer=request.headers.get('Referer','')[:500], is_admin=False)
        db.session.add(pv)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    if is_new_visitor_cookie:
        from flask import g
        g.new_visitor_id = visitor_id

@public_bp.after_app_request
def set_visitor_cookie(response):
    from flask import g
    if hasattr(g, 'new_visitor_id'):
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
        if request.form.get('website'):
            return render_template('contact.html', settings=settings, services=services_list, error="Spam detected")
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        service_interest = request.form.get('service_interest','').strip()
        message = request.form.get('message','').strip()
        errors = []
        if not name or len(name)<2:
            errors.append("Name must be at least 2 characters")
        if not email or '@' not in email:
            errors.append("Valid email required")
        if not message or len(message)<10:
            errors.append("Message must be at least 10 characters")
        if errors:
            return render_template('contact.html', settings=settings, services=services_list, errors=errors, form_data=request.form)
        try:
            cm = ContactMessage(name=name[:200], email=email[:200], service_interest=service_interest[:200], message=message[:5000], ip_address=get_client_ip())
            db.session.add(cm)
            db.session.commit()
            return render_template('contact.html', settings=settings, services=services_list, success=True)
        except:
            db.session.rollback()
            return render_template('contact.html', settings=settings, services=services_list, error="Failed to send message.")
    return render_template('contact.html', settings=settings, services=services_list)

@public_bp.route('/privacy')
def privacy():
    settings = get_settings_dict()
    return render_template('privacy.html', settings=settings)

@public_bp.route('/robots.txt')
def robots():
    site_url = current_app.config.get('SITE_URL','')
    content = f"User-agent: *\nAllow: /\n\nSitemap: {site_url}/sitemap.xml\n"
    return current_app.response_class(content, mimetype='text/plain')

@public_bp.route('/sitemap.xml')
def sitemap():
    settings = get_settings_dict()
    site_url = current_app.config.get('SITE_URL','http://localhost:5000').rstrip('/')
    pages = [
        {'loc': f"{site_url}/", 'priority': '1.0'},
        {'loc': f"{site_url}/services", 'priority': '0.9'},
        {'loc': f"{site_url}/projects", 'priority': '0.9'},
        {'loc': f"{site_url}/tools/sensitivity", 'priority': '0.95'},
        {'loc': f"{site_url}/tools/free-fire-sensitivity", 'priority': '0.95'},
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

# --- SENSI LAB TOOL ---
@public_bp.route('/tools/sensitivity')
@public_bp.route('/tools/free-fire-sensitivity')
@public_bp.route('/free-fire-sensitivity')
def sensitivity_tool():
    settings = get_settings_dict()
    # get avg rating
    avg = db.session.query(db.func.avg(SensitivityReview.rating)).filter(SensitivityReview.is_approved==True).scalar()
    count = SensitivityReview.query.filter_by(is_approved=True).count()
    recent_reviews = SensitivityReview.query.filter_by(is_approved=True).order_by(SensitivityReview.created_at.desc()).limit(20).all()
    return render_template('tools/sensitivity.html', settings=settings, avg_rating=round(avg,1) if avg else 0, rating_count=count, reviews=recent_reviews)

@public_bp.route('/api/sensitivity/generate', methods=['POST'])
def api_sensitivity_generate():
    try:
        from app.utils.sensitivity_engine import generate_sensitivity
        data = request.get_json() or request.form or {}
        profile = {
            'brand': data.get('brand','others'),
            'ram': data.get('ram',4),
            'iphone_model': data.get('iphone_model',''),
            'playstyle': data.get('playstyle',3),
            'gyro': data.get('gyro','none'),
            'role': data.get('role','balanced'),
            'experience': data.get('experience','intermediate')
        }
        result = generate_sensitivity(profile)
        return jsonify({'ok':True, 'result':result})
    except Exception as e:
        return jsonify({'ok':False, 'error':str(e)}), 400

@public_bp.route('/api/sensitivity/rate', methods=['POST'])
def api_sensitivity_rate():
    try:
        data = request.get_json() or {}
        rating = int(data.get('rating',0))
        if rating <1 or rating>5:
            return jsonify({'ok':False, 'error':'Rating must be 1-5'}), 400
        comment = (data.get('comment','') or '').strip()[:1000]
        author_name = (data.get('author_name','') or '').strip()[:100]
        brand = data.get('brand','others')[:50]
        ram_raw = data.get('ram',4)
        try:
            ram = int(ram_raw)
        except:
            ram = 4
        iphone_model = data.get('iphone_model','')[:50]
        playstyle = int(data.get('playstyle',3))
        gyro = data.get('gyro','none')[:20]
        role = data.get('role','balanced')[:20]
        experience = data.get('experience','intermediate')[:20]
        # generated values
        general = int(data.get('general',0) or 0)
        red_dot = int(data.get('red_dot',0) or 0)
        scope_2x = int(data.get('scope_2x',0) or 0)
        scope_4x = int(data.get('scope_4x',0) or 0)
        sniper = int(data.get('sniper',0) or 0)
        free_look = int(data.get('free_look',0) or 0)
        dpi = int(data.get('dpi',0) or 0)

        # simple spam protection: one review per IP per 5 mins
        ip = get_client_ip()
        recent = SensitivityReview.query.filter(SensitivityReview.ip_address==ip, SensitivityReview.created_at>=datetime.now(timezone.utc)-timedelta(minutes=5)).first()
        if recent:
            return jsonify({'ok':False, 'error':'You rated recently, wait 5 mins'}), 429

        rev = SensitivityReview(
            brand=brand, ram=ram, iphone_model=iphone_model, playstyle=playstyle, gyro=gyro, role=role, experience=experience,
            general=general, red_dot=red_dot, scope_2x=scope_2x, scope_4x=scope_4x, sniper=sniper, free_look=free_look, dpi=dpi,
            rating=rating, comment=comment, author_name=author_name, ip_address=ip, is_approved=True
        )
        db.session.add(rev)
        db.session.commit()
        return jsonify({'ok':True, 'message':'Thanks! Rating saved'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok':False, 'error':str(e)}), 400

@public_bp.route('/api/sensitivity/reviews', methods=['GET'])
def api_sensitivity_reviews():
    try:
        brand_filter = request.args.get('brand')
        q = SensitivityReview.query.filter_by(is_approved=True)
        if brand_filter:
            q = q.filter_by(brand=brand_filter)
        reviews = q.order_by(SensitivityReview.created_at.desc()).limit(50).all()
        avg = db.session.query(db.func.avg(SensitivityReview.rating)).filter(SensitivityReview.is_approved==True).scalar()
        data = []
        for r in reviews:
            data.append({
                'id': r.id,
                'brand': r.brand,
                'iphone_model': r.iphone_model,
                'ram': r.ram,
                'playstyle': r.playstyle,
                'role': r.role,
                'rating': r.rating,
                'comment': r.comment,
                'author_name': r.author_name or 'Anonymous',
                'general': r.general,
                'red_dot': r.red_dot,
                'created_at': r.created_at.isoformat() if r.created_at else ''
            })
        return jsonify({'ok':True, 'avg': round(avg,1) if avg else 0, 'count': len(data), 'reviews': data})
    except Exception as e:
        return jsonify({'ok':False, 'error':str(e)}), 400

@public_bp.route('/api/track', methods=['POST'])
def api_track():
    return jsonify({'ok':True})
