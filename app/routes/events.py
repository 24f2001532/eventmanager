from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Event, Registration, Notification

bp = Blueprint('events', __name__)

@bp.route('/')
@login_required
def list_events():
    events = Event.query.order_by(Event.event_date.asc()).all()
    return render_template('events/list.html', events=events)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role != 'organizer':
        flash('Only organizers can create events.', 'error')
        return redirect(url_for('events.list_events'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        event_date_str = request.form.get('event_date')
        registration_deadline_str = request.form.get('registration_deadline')
        max_registrations = request.form.get('max_registrations')
        
        if not all([title, description, location, event_date_str, registration_deadline_str]):
            flash('Please fill in all required fields.', 'error')
            return render_template('events/create.html')
        
        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
            registration_deadline = datetime.strptime(registration_deadline_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.', 'error')
            return render_template('events/create.html')
        
        if registration_deadline >= event_date:
            flash('Registration deadline must be before event date.', 'error')
            return render_template('events/create.html')
        
        if registration_deadline < datetime.utcnow():
            flash('Registration deadline cannot be in the past.', 'error')
            return render_template('events/create.html')
        
        max_reg = int(max_registrations) if max_registrations else None
        
        event = Event(
            title=title,
            description=description,
            location=location,
            event_date=event_date,
            registration_deadline=registration_deadline,
            max_registrations=max_reg,
            organizer_id=current_user.id
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.list_events'))
    
    return render_template('events/create.html')

@bp.route('/<int:event_id>')
@login_required
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    is_registered = Registration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first() is not None
    
    return render_template('events/view.html', event=event, is_registered=is_registered)

@bp.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if already registered
    existing_registration = Registration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if existing_registration:
        flash('You are already registered for this event.', 'info')
        return redirect(url_for('events.view_event', event_id=event_id))
    
    # Check if registration is open
    if not event.is_registration_open:
        flash('Registration for this event is closed.', 'error')
        return redirect(url_for('events.view_event', event_id=event_id))
    
    # Check if event is full
    if event.is_full:
        flash('This event is full.', 'error')
        return redirect(url_for('events.view_event', event_id=event_id))
    
    # Create registration
    registration = Registration(
        user_id=current_user.id,
        event_id=event_id
    )
    
    db.session.add(registration)
    
    # Create notification
    notification = Notification(
        user_id=current_user.id,
        event_id=event_id,
        message=f'You have successfully registered for "{event.title}"',
        notification_type='registration_confirmation'
    )
    db.session.add(notification)
    
    db.session.commit()
    
    flash('Successfully registered for the event!', 'success')
    return redirect(url_for('events.view_event', event_id=event_id))

@bp.route('/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_registration(event_id):
    registration = Registration.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if registration:
        db.session.delete(registration)
        db.session.commit()
        flash('Registration cancelled successfully.', 'success')
    else:
        flash('You are not registered for this event.', 'error')
    
    return redirect(url_for('events.view_event', event_id=event_id))

@bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if current_user.id != event.organizer_id and current_user.role != 'organizer':
        flash('You do not have permission to edit this event.', 'error')
        return redirect(url_for('events.view_event', event_id=event_id))
    
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.location = request.form.get('location')
        event_date_str = request.form.get('event_date')
        registration_deadline_str = request.form.get('registration_deadline')
        max_registrations = request.form.get('max_registrations')
        
        try:
            event.event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
            event.registration_deadline = datetime.strptime(registration_deadline_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.', 'error')
            return render_template('events/edit.html', event=event)
        
        event.max_registrations = int(max_registrations) if max_registrations else None
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.view_event', event_id=event_id))
    
    return render_template('events/edit.html', event=event)

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if current_user.id != event.organizer_id and current_user.role != 'organizer':
        flash('You do not have permission to delete this event.', 'error')
        return redirect(url_for('events.view_event', event_id=event_id))
    
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully.', 'success')
    return redirect(url_for('events.list_events'))

@bp.route('/registrations/count/<int:event_id>')
@login_required
def get_registration_count(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify({
        'count': event.registration_count,
        'max': event.max_registrations,
        'is_full': event.is_full,
        'is_open': event.is_registration_open
    })

