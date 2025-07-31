from app import app, db
from models import User
import os

with app.app_context():
    db.create_all()

    # Create admin if not exists
    if not User.query.filter_by(role='admin').first():
        admin = User(
            name=os.getenv('ADMIN_NAME'),
            email=os.getenv('ADMIN_EMAIL'),
            role='admin',
            user_pincode='000000'  # Default pincode for admin
        )
        admin.set_password(os.getenv('ADMIN_PASSWORD'))
        db.session.add(admin)
        db.session.commit()
        print(f"[INIT] Admin created: {admin.email}")
    else:
        print("[INIT] Admin already exists.")

    print('Database initialized!')
