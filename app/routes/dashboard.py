from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import Event, Registration, Notification

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'organizer':
        # Organizer dashboard
        my_events = Event.query.filter_by(organizer_id=current_user.id)\
            .order_by(Event.event_date.asc()).all()
        
        upcoming_events = Event.query.filter(
            Event.event_date > datetime.utcnow(),
            Event.organizer_id == current_user.id
        ).order_by(Event.event_date.asc()).limit(5).all()
        
        total_events = len(my_events)
        total_registrations = sum(event.registration_count for event in my_events)
        
        return render_template('dashboard/organizer.html',
                             events=my_events,
                             upcoming_events=upcoming_events,
                             total_events=total_events,
                             total_registrations=total_registrations)
    else:
        # User dashboard
        my_registrations = Registration.query.filter_by(user_id=current_user.id)\
            .join(Event)\
            .order_by(Event.event_date.asc()).all()
        
        upcoming_registrations = [
            reg for reg in my_registrations
            if reg.event.event_date > datetime.utcnow()
        ][:5]
        
        all_events = Event.query.filter(Event.event_date > datetime.utcnow())\
            .order_by(Event.event_date.asc()).all()
        
        registered_event_ids = {reg.event_id for reg in my_registrations}
        
        return render_template('dashboard/user.html',
                             registrations=my_registrations,
                             upcoming_registrations=upcoming_registrations,
                             all_events=all_events,
                             registered_event_ids=registered_event_ids)

@bp.route('/notifications')
@login_required
def notifications():
    user_notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).all()
    
    return render_template('dashboard/notifications.html', notifications=user_notifications)

@bp.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = True
    from app import db
    db.session.commit()
    
    return jsonify({'success': True})

@bp.route('/notifications/unread-count')
@login_required
def unread_notifications_count():
    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify({'count': count})

