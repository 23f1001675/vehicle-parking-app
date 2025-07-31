from mailer import send_email
from models import User, Reservation, ParkingLot
import datetime
from flask import current_app
from sqlalchemy import func
from celery import shared_task

@shared_task(name="send_monthly_reports")
def send_monthly_reports():
    with current_app.app_context():
        today = datetime.date.today()
        first_day = today.replace(day=1)
        last_month_start = (first_day - datetime.timedelta(days=1)).replace(day=1)
        last_month_end = first_day - datetime.timedelta(days=1)

        users = User.query.all()
        for u in users:
            reservations = Reservation.query.filter(
                Reservation.user_id == u.id,
                Reservation.booked_at >= last_month_start,
                Reservation.booked_at <= last_month_end
            ).all()

            total_cost = sum(r.parking_cost or 0 for r in reservations)

            most_used = (
                Reservation.query.join(ParkingLot, Reservation.spot_id == ParkingLot.id)
                .with_entities(ParkingLot.city, func.count(Reservation.id))
                .filter(
                    Reservation.user_id == u.id,
                    Reservation.booked_at >= last_month_start,
                    Reservation.booked_at <= last_month_end
                )
                .group_by(ParkingLot.city)
                .order_by(func.count(Reservation.id).desc())
                .first()
            )

            html_report = f"""
            <h2>Monthly Parking Report ({last_month_start.strftime('%B %Y')})</h2>
            <p><b>Total reservations:</b> {len(reservations)}</p>
            <p><b>Total spent:</b> ₹{total_cost:.2f}</p>
            <p><b>Most used lot:</b> {most_used[0] if most_used else "N/A"}</p>
            """
            print(f"📧 Sending report to receiver@test.com with {len(reservations)} reservations")
            send_email(
                "receiver@test.com",
                subject=f"Parking Report - {last_month_start.strftime('%B %Y')}",
                message=html_report
            )
            send_email("receiver@test.com", subject=f"Parking Report - {last_month_start.strftime('%B %Y')}", message=html_report)
