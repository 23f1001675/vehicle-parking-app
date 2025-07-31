import os
from flask import Flask # type: ignore
from flask_jwt_extended import JWTManager   # type: ignore
from dotenv import load_dotenv # type: ignore
from flask_cors import CORS # type: ignore
from datetime import timedelta
from caching import cache
from flask import send_from_directory
import redis
from models import db
from celery_init import celery_init_app
from celery.schedules import crontab
from flask_mail import Mail
import jobs.exports
import jobs.reports

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp



# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicle_parking.db'
app.config['INSTANCE_PATH'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)


db.init_app(app)
jwt = JWTManager(app)
cache.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(user_bp, url_prefix='/api/user')

@app.route('/exports/<filename>')
def download_export(filename):
    return send_from_directory("static/exports", filename, as_attachment=True)

celery = celery_init_app(app)
celery.autodiscover_tasks()
celery.conf.beat_schedule = {
    "send-monthly-reports": {
        "task": "send_monthly_reports",
        # "schedule": crontab(hour=9, minute=0, day_of_month=1),  # 1st day @ 9 AM
        "schedule": crontab(hour="*", minute="*/1", day_of_month="31"),
    }
}

if __name__ == '__main__':
    app.run(port=5000, debug=True)
