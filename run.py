from app import create_app, db
from app.models import User, Event, Registration, Notification

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create a default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='organizer'
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin123'")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

