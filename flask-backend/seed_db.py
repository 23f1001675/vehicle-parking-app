from app import app, db
from models import User, ParkingLot, ParkingSpot, Reservation
from werkzeug.security import generate_password_hash # type: ignore
from datetime import datetime, timedelta
import random
import pytz # type: ignore

IST = pytz.timezone("Asia/Kolkata")
hashed_pw = generate_password_hash("password123")

def seed():
    with app.app_context():
        print(" Starting DB seeding...")
        # Create Users
        users = []
        for i in range(1, 4):
            u = User(
                name=f"User{i}",
                email=f"user{i}@mail.com",
                password_hash=generate_password_hash("user123"),
                role="user",
                user_pincode=f"5000{i}"
            )
            users.append(u)
            db.session.add(u)
        db.session.commit()

        now = datetime.now(IST)
        print(now)
        
        # --- Create 3 Lots (1 per user) ---
        for idx, user in enumerate(users, start=1):
            lot = ParkingLot(
                city="Hyderabad",
                address=f"Lot {idx} - Test Area",
                pincode=f"5000{idx}",
                price=20 * idx,  # 20, 40, 60
                number_of_spots=50  # 6 spots per lot
            )
            db.session.add(lot)
            db.session.flush()

            # Create 6 spots
            for j in range(1, 51):
                spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(spot)
                db.session.flush()

                # Assign 2 reserved, 2 occupied, 2 available
                if j in [1, 2]:  # Reserved
                    spot.status = 'R'
                    reservation = Reservation(
                        user_id=user.id,
                        spot_id=spot.id,
                        vehicle_number=f"ABC{1000 + j}",
                        booked_at=now - timedelta(hours=1),
                        parking_timestamp=None,
                        leaving_timestamp=None,
                        parking_cost=None
                    )
                    db.session.add(reservation)

                elif j in [3, 4]:  # Occupied
                    spot.status = 'O'
                    reservation = Reservation(
                        user_id=user.id,
                        spot_id=spot.id,
                        vehicle_number=f"XYZ{2000 + j}",
                        booked_at=now - timedelta(hours=3),
                        parking_timestamp=now - timedelta(hours=2),
                        leaving_timestamp=None,
                        parking_cost=None
                    )
                    db.session.add(reservation)

                else:  # Available (no reservation)
                    spot.status = 'A'

        db.session.commit()
        print("✅ DB seeded successfully!")

if __name__ == "__main__":
    seed()
