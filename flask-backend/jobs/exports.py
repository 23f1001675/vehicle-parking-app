import csv
import datetime
import os
from celery import shared_task
from flask import current_app
from models import Reservation

@shared_task(ignore_results=False, name="download_csv_report")
def csv_report(user_id):
    """Generate CSV of reservations for a given user."""
    with current_app.app_context():
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        if not reservations:
            return None

        # unique filename
        csv_file_name = f"reservations_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        file_path = os.path.join("static", csv_file_name)

        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "Sr No.", "Reservation ID", "User ID", "Spot ID", "Vehicle Number",
                "Booked At", "Parking Timestamp", "Leaving Timestamp", "Parking Cost"
            ])

            for idx, res in enumerate(reservations, start=1):
                booked_ts = res.booked_at.strftime("%Y-%m-%d %H:%M:%S") if res.booked_at else ""
                parking_ts = res.parking_timestamp.strftime("%Y-%m-%d %H:%M:%S") if res.parking_timestamp else ""
                leaving_ts = res.leaving_timestamp.strftime("%Y-%m-%d %H:%M:%S") if res.leaving_timestamp else ""

                writer.writerow([
                    idx,
                    res.id,
                    res.user_id,
                    res.spot_id,
                    res.vehicle_number,
                    booked_ts,
                    parking_ts,
                    leaving_ts,
                    f"{res.parking_cost:.2f}" if res.parking_cost else "0.00"
                ])

        return csv_file_name
