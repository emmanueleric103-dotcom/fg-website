# FG (HefGe) — Personal Digital Services Website

Production-ready portfolio for **FG (HefGe)** — dark futuristic theme, real visitor analytics, secure admin dashboard.

## Features
- Public: Home, Services (8 services), Projects, About, Contact, Privacy, sitemap, robots.txt
- Admin at `/admin`: login, overview (today/week/total, 7-day chart, top pages, recent messages), analytics (7/30/90 days), services CRUD, projects CRUD, contact management, site settings, password change
- Real analytics: first-party `fg_visitor_id` cookie, page views vs unique visitors, 30s throttle, admin traffic excluded, timezone Africa/Lagos, DailyStat aggregation
- Security: PBKDF2 hashed passwords, session cookies HttpOnly + SameSite, CSRF tokens, rate limiting (5 attempts /5min), honeypot + validation, no secrets in JS
- No fake data: placeholders clearly marked, admin must configure real contacts/socials

## Stack
Python Flask 3, Flask-SQLAlchemy, SQLite (Postgres compatible via DATABASE_URL), Jinja, vanilla JS, Gunicorn

## Quick Start (Termux / Local)

```bash
# 1. Clone / copy project
cd fg-hefge-website

# 2. Python env
python -m venv venv
source venv/bin/activate  # Termux: source venv/bin/activate

# 3. Install
pip install -r requirements.txt

# 4. Env file
cp .env.example .env
# Edit .env: set SECRET_KEY (32+ chars), ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL, SITE_URL=http://localhost:5000

# 5. Init DB + admin + default services
export FLASK_APP=wsgi.py
flask init-db

# 6. Run
python run.py
# or
flask run --host=0.0.0.0 --port=5000
```

Visit http://localhost:5000 — admin at http://localhost:5000/admin

## Termux Specific

```bash
pkg update && pkg upgrade
pkg install python git
# optional: pkg install clang libffi openssl (for building)
pip install --upgrade pip
pip install -r requirements.txt
# Set env
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=YourStrongPass123!
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
flask init-db
python run.py
# Then open localhost:5000 in browser
```

## Environment Variables

| Key | Required | Description |
|-----|----------|-------------|
| SECRET_KEY | Yes | 32+ random chars |
| DATABASE_URL | No | sqlite:///instance/fg_website.db or postgres://... (Render auto) |
| ADMIN_USERNAME | Yes | Initial admin username |
| ADMIN_PASSWORD | Yes | Initial admin password (hashed on creation, never stored plain) |
| ADMIN_EMAIL | No | Admin email |
| SITE_URL | No | For sitemap, OG tags |
| TIMEZONE | No | Default Africa/Lagos |
| ANALYTICS_RETENTION_DAYS | No | Default 90 |

**Never commit `.env`**

## Admin Setup

- Initial admin created via `flask init-db` using env vars. No public registration.
- Change password: Admin → Settings → Change password form.
- To create another admin, use Flask shell:
```python
from app import create_app
from app.extensions import db
from app.models import Admin
app = create_app()
with app.app_context():
    a=Admin(username='newadmin', email='new@example.com')
    a.set_password('StrongPass!')
    db.session.add(a)
    db.session.commit()
```

## Configure Your Real Info (No Fake Data)

1. Login /admin
2. Go to Settings
3. Fill: WhatsApp number (format 2348012345678, no +), Telegram URL, email, GitHub, etc.
4. Save — appears instantly on public site.

Services and Projects: Admin → Services / Projects → New. You can reorder via order_index.

Homepage headline: Settings → Homepage headline/subheadline.

## Analytics Testing

1. Open site in incognito (not logged as admin)
2. Browse /, /services, /projects
3. Check /admin/ → overview — you should see today views increment
4. Refresh within 30s on same page — should NOT count again (throttle)
5. Login as admin and browse — should NOT count (admin excluded)
6. Chart: uses real DailyStat + live PageView fallback. Run aggregation: POST /admin/api/aggregate with CSRF token or via Overview → Refresh stats

## Database

- SQLite at `instance/fg_website.db` (auto-created)
- For Render/ephemeral: set DATABASE_URL to managed Postgres, or configure disk persistence. Code already handles both.
- Tables: admins, services, projects, visitors, page_views, daily_stats, contact_messages, site_settings
- Indexes on visitor_id, page_path, timestamp, slug, status

## Deployment (Render)

1. Push to GitHub
2. Render → New Web Service → connect repo
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app`
5. Add env vars: SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL, SITE_URL, DATABASE_URL (Render Postgres)
6. Add persistent disk if staying on SQLite (not recommended) — or use Render Postgres
7. Deploy → SSH → `flask init-db`
8. Set SITE_URL to your public URL for sitemap OG

`Procfile` and `requirements.txt` already included.

## Security Checklist

- [x] Passwords hashed PBKDF2
- [x] No admin registration
- [x] CSRF tokens on all POST forms
- [x] Rate limiting login
- [x] Session HttpOnly SameSite Lax, Secure in prod
- [x] No secrets in frontend JS
- [x] Admin excluded from analytics
- [x] Contact honeypot + server validation
- [x] No private data exposed to public endpoints

## Tests

```bash
pytest tests/ -v
```

Covers: public pages, admin auth, protected endpoints, contact validation, visitor tracking, unique counting, weekly stats, admin exclusion, DB init, security.

## What Works / What To Configure

**Works out of box:**
- All public pages, responsive, dark futuristic theme
- Services CRUD + publish toggle + reorder
- Projects CRUD + featured
- Contact form with validation + spam protection
- Admin auth + rate limit + password change
- Real analytics tracking + charts (Chart.js CDN)
- Sitemap, robots.txt, OG tags, 404/500

**You must configure before publishing:**
- Set real SECRET_KEY
- Set ADMIN_USERNAME/PASSWORD via env and run init-db
- In Admin Settings, set real WhatsApp, Telegram, email, social URLs (currently empty placeholders)
- Add your real projects (currently empty — no fake invented)
- Set SITE_URL to your domain
- For production, use Postgres DATABASE_URL and set SESSION_COOKIE_SECURE=True via FLASK_ENV=production

## License
Private for FG (HefGe)
