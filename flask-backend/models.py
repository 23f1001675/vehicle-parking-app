from flask_sqlalchemy import SQLAlchemy # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
import pytz # type: ignore
from datetime import datetime

db = SQLAlchemy()
IST = pytz.timezone("Asia/Kolkata")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    date_created = db.Column(db.DateTime, server_default=db.func.now())
    user_pincode = db.Column(db.String(6), nullable=False)
    
    # Relationship: A user can have many reservations
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200))
    pincode = db.Column(db.String(10))
    price = db.Column(db.Float)
    number_of_spots = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, server_default=db.func.now())

    # Relationship: A parking lot can have many parking spots
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade="all, delete")

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), default='A')  # 'A' for Available, 'O' for Occupied, 'R' for Reserved
    
    # Relationship: A parking spot can have one reservation
    current_reservation = db.relationship('Reservation', uselist=False, backref='spot', lazy=True)


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=True)
    booked_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(IST))
    parking_timestamp = db.Column(db.DateTime(timezone=True))
    leaving_timestamp = db.Column(db.DateTime(timezone=True))
    parking_cost = db.Column(db.Float)