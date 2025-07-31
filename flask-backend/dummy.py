from app import app, db
from models import User, ParkingLot, ParkingSpot, Reservation
from werkzeug.security import generate_password_hash # type: ignore
from datetime import datetime, timedelta
import random 
import pytz # type: ignore

IST = pytz.timezone("Asia/Kolkata")

def seed():
    with app.app_context():
        print("Create new reservations with booking_at timestamps for each day increasingly (1 on first day, 2 on second day, etc.) for user ID 1 only and whichever spot is available (not same spot every day).")
        user = User.query.filter_by(id=2).first()
        if not user:
            print("User with ID 1 not found.")
            return
        now = datetime.now(IST)
        for i in range(1, 8):  # Create reservations for 7 days
            reservation_date = now + timedelta(days=i)
            available_spots = ParkingSpot.query.filter_by(status='A').all()
            if not available_spots:
                print(f"No available spots for day {i}.")
                continue
            #Spot should not repeat for the same user
            # Randomly select an available spot
            spot = random.choice(available_spots)
            if spot.status == 'A':
                spot.status = 'R'
                reservation = Reservation(
                    user_id=user.id,
                    spot_id=spot.id,
                    vehicle_number=f"ABC{1000 + i}",
                    booked_at=reservation_date,
                    parking_timestamp=None,
                    leaving_timestamp=None,
                    parking_cost=None
                )
                db.session.add(reservation)
                db.session.commit()
        print("Reservations created successfully.")
        
if __name__ == "__main__":
    seed()
