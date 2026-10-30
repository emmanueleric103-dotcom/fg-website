from datetime import datetime, timezone, timedelta, date
from zoneinfo import ZoneInfo
from sqlalchemy import func
from app.extensions import db
from app.models import PageView, Visitor, DailyStat, ContactMessage, SiteSetting
import json

def get_tz():
    try:
        return ZoneInfo('Africa/Lagos')
    except:
        return ZoneInfo('UTC')

def get_today_range():
    tz = get_tz()
    now = datetime.now(tz)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    # Convert to UTC for DB query since we store UTC
    start_utc = start.astimezone(timezone.utc)
    end_utc = end.astimezone(timezone.utc)
    return start_utc, end_utc, start.date()

def get_date_range(days):
    tz = get_tz()
    now = datetime.now(tz)
    end = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    start = end - timedelta(days=days)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)

def aggregate_daily_stats(target_date=None):
    """Aggregate stats for a specific date (date object) or today"""
    tz = get_tz()
    if target_date is None:
        target_date = datetime.now(tz).date()
    
    # Range in UTC
    start_local = datetime.combine(target_date, datetime.min.time(), tzinfo=tz)
    end_local = start_local + timedelta(days=1)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)
    
    total_views = PageView.query.filter(
        PageView.timestamp >= start_utc,
        PageView.timestamp < end_utc,
        PageView.is_admin == False
    ).count()
    
    unique_visitors = db.session.query(func.count(func.distinct(PageView.visitor_id))).filter(
        PageView.timestamp >= start_utc,
        PageView.timestamp < end_utc,
        PageView.is_admin == False
    ).scalar() or 0
    
    # Top pages
    top_pages_q = db.session.query(
        PageView.page_path, func.count(PageView.id).label('cnt')
    ).filter(
        PageView.timestamp >= start_utc,
        PageView.timestamp < end_utc,
        PageView.is_admin == False
    ).group_by(PageView.page_path).order_by(func.count(PageView.id).desc()).limit(10).all()
    
    top_pages = [{'path': p[0], 'count': p[1]} for p in top_pages_q]
    
    # Top services
    top_services_q = db.session.query(
        PageView.page_path, func.count(PageView.id).label('cnt')
    ).filter(
        PageView.timestamp >= start_utc,
        PageView.timestamp < end_utc,
        PageView.page_path.like('/services%'),
        PageView.is_admin == False
    ).group_by(PageView.page_path).order_by(func.count(PageView.id).desc()).limit(10).all()
    
    top_services = [{'path': p[0], 'count': p[1]} for p in top_services_q]
    
    # Upsert DailyStat
    existing = DailyStat.query.filter_by(date=target_date).first()
    if existing:
        existing.total_views = total_views
        existing.unique_visitors = unique_visitors
        existing.top_pages = json.dumps(top_pages)
        existing.top_services = json.dumps(top_services)
    else:
        existing = DailyStat(
            date=target_date,
            total_views=total_views,
            unique_visitors=unique_visitors,
            top_pages=json.dumps(top_pages),
            top_services=json.dumps(top_services)
        )
        db.session.add(existing)
    db.session.commit()
    return existing

def get_overview_stats():
    tz = get_tz()
    today = datetime.now(tz).date()
    
    # Today
    start_utc, end_utc, _ = get_today_range()
    today_views = PageView.query.filter(
        PageView.timestamp >= start_utc,
        PageView.timestamp < end_utc,
        PageView.is_admin == False
    ).count()
    today_unique = db.session.query(func.count(func.distinct(PageView.visitor_id))).filter(
        PageView.timestamp >= start_utc,
        PageView.timestamp < end_utc,
        PageView.is_admin == False
    ).scalar() or 0
    
    # Last 7 days
    start_7, end_7 = get_date_range(7)
    week_views = PageView.query.filter(
        PageView.timestamp >= start_7,
        PageView.timestamp < end_7,
        PageView.is_admin == False
    ).count()
    week_unique = db.session.query(func.count(func.distinct(PageView.visitor_id))).filter(
        PageView.timestamp >= start_7,
        PageView.timestamp < end_7,
        PageView.is_admin == False
    ).scalar() or 0
    
    # Total
    total_views = PageView.query.filter_by(is_admin=False).count()
    total_unique = db.session.query(func.count(func.distinct(PageView.visitor_id))).filter(
        PageView.is_admin == False
    ).scalar() or 0
    
    # Chart data last 7 days
    chart_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        stat = DailyStat.query.filter_by(date=d).first()
        if stat:
            chart_data.append({
                'date': d.strftime('%b %d'),
                'views': stat.total_views,
                'unique': stat.unique_visitors
            })
        else:
            # Fallback live query
            sd = datetime.combine(d, datetime.min.time(), tzinfo=tz).astimezone(timezone.utc)
            ed = sd + timedelta(days=1)
            v = PageView.query.filter(PageView.timestamp >= sd, PageView.timestamp < ed, PageView.is_admin==False).count()
            u = db.session.query(func.count(func.distinct(PageView.visitor_id))).filter(PageView.timestamp >= sd, PageView.timestamp < ed, PageView.is_admin==False).scalar() or 0
            chart_data.append({'date': d.strftime('%b %d'), 'views': v, 'unique': u})
    
    # Most visited pages overall
    most_pages = db.session.query(
        PageView.page_path, func.count(PageView.id).label('cnt')
    ).filter(PageView.is_admin==False).group_by(PageView.page_path).order_by(func.count(PageView.id).desc()).limit(10).all()
    
    most_pages_list = [{'path': p[0], 'count': p[1]} for p in most_pages]
    
    # Recent contacts
    recent_contacts = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    return {
        'today_views': today_views,
        'today_unique': today_unique,
        'week_views': week_views,
        'week_unique': week_unique,
        'total_views': total_views,
        'total_unique': total_unique,
        'chart_data': chart_data,
        'most_pages': most_pages_list,
        'recent_contacts': recent_contacts
    }

def get_analytics_range(days=7):
    tz = get_tz()
    today = datetime.now(tz).date()
    data = []
    for i in range(days-1, -1, -1):
        d = today - timedelta(days=i)
        stat = DailyStat.query.filter_by(date=d).first()
        if stat:
            tp = json.loads(stat.top_pages) if stat.top_pages else []
            data.append({
                'date': d.isoformat(),
                'label': d.strftime('%Y-%m-%d'),
                'short': d.strftime('%b %d'),
                'views': stat.total_views,
                'unique': stat.unique_visitors,
                'top_pages': tp
            })
        else:
            sd = datetime.combine(d, datetime.min.time(), tzinfo=tz).astimezone(timezone.utc)
            ed = sd + timedelta(days=1)
            v = PageView.query.filter(PageView.timestamp >= sd, PageView.timestamp < ed, PageView.is_admin==False).count()
            u = db.session.query(func.count(func.distinct(PageView.visitor_id))).filter(PageView.timestamp >= sd, PageView.timestamp < ed, PageView.is_admin==False).scalar() or 0
            data.append({
                'date': d.isoformat(),
                'label': d.strftime('%Y-%m-%d'),
                'short': d.strftime('%b %d'),
                'views': v,
                'unique': u,
                'top_pages': []
            })
    return data
