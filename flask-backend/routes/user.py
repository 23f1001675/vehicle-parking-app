from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timezone
from caching import cache
import pytz
from jobs.exports import csv_report
from celery.result import AsyncResult
from jobs.reports import send_monthly_reports
from flask import send_file
import os


user_bp = Blueprint('user', __name__)
IST = pytz.timezone("Asia/Kolkata")

# Helper to check user role
def user_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "user":
            return jsonify({"msg": "Users only!"}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

# Get all Parking Lots
@user_bp.route('/get-all-lots', methods=['GET'])
@jwt_required()
def get_all_lots():
    lots = ParkingLot.query.all()
    data = []
    for lot in lots:
        data.append({
            "id": lot.id,
            "city": lot.city,
            "address": lot.address,
            "pincode": lot.pincode,
            "price": lot.price,
            "total_spots": lot.number_of_spots,
            "available_spots": len([spot for spot in lot.spots if spot.status == 'A']),
            "date_created": lot.date_created.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(data), 200

# Get user details
@user_bp.route('/get-user-details/<int:user_id>', methods=['GET'])
@user_required
def get_user_details(user_id):
    user = User.query.get_or_404(user_id)
    data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "user_pincode": user.user_pincode,
        "date_joined": user.date_created.strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify(data), 200

# Reserve a parking spot
@user_bp.route('/reserve-spot/<int:lot_id>', methods=['POST'])
@jwt_required()
@user_required
def reserve_spot(lot_id):
    claims = get_jwt()
    # print(claims.get("sub"))
    user_id = claims.get("sub") or claims.get("id")
    vehicle_number = request.json.get('vehicle_number')
    lot = ParkingLot.query.get_or_404(lot_id)
    available_spots = [spot for spot in lot.spots if spot.status == 'A']
    if not available_spots:
        return jsonify({"msg": "No available spots in this lot"}), 400
    
    spot = available_spots[0]
    spot.status = 'R'
    reservation = Reservation(user_id=user_id, spot_id=spot.id, vehicle_number=vehicle_number)
    db.session.add(reservation)
    db.session.commit()

    return jsonify({"msg": "Spot reserved successfully!", "spot_id": spot.id, "vehicle_number": vehicle_number}), 200

# Get user's reservations
@user_bp.route('/my-reservations', methods=['GET'])
@jwt_required()
@user_required
@cache.cached(timeout=60, query_string=True)
def my_reservations():
    claims = get_jwt()
    # print(claims)
    user_id = claims.get("sub") or claims.get("id")

    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.booked_at.desc()).all()
    data = []
    for res in reservations:
        spot = ParkingSpot.query.get(res.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        data.append({
            "reservation_id": res.id,
            "spot_id": res.spot_id,
            "lot_id": lot.id,
            "lot_cost": lot.price,
            "lot_city": lot.city,
            "lot_address": lot.address,
            "vehicle_number": res.vehicle_number,
            "booked_at": res.booked_at.strftime('%Y-%m-%d %H:%M:%S') if res.booked_at else None,
            "parking_timestamp": res.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.parking_timestamp else None,
            "leaving_timestamp": res.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.leaving_timestamp else None,
            "parking_cost": res.parking_cost
        })
    return jsonify(data), 200

# Mark a reserved spot as occupied
@user_bp.route('/occupy-reserved-spot/<int:reservation_id>', methods=['POST'])
@jwt_required()
@user_required
def occupy_reserved_spot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.parking_timestamp is not None:
        return jsonify({"msg": "Spot already occupied"}), 400

    spot = ParkingSpot.query.get_or_404(reservation.spot_id)
    if spot.status != 'R':
        return jsonify({"msg": "Spot is not in reserved state"}), 400

    spot.status = 'O'
    reservation.parking_timestamp = datetime.now(IST).replace(tzinfo=None)

    db.session.commit()
    return jsonify({"msg": "Spot marked as occupied"}), 200

# Release a parking spot
@user_bp.route('/release-spot/<int:reservation_id>', methods=['POST'])
@jwt_required()
@user_required
def release_spot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.leaving_timestamp is not None:
        return jsonify({"msg": "Spot already released"}), 400

    spot = ParkingSpot.query.get_or_404(reservation.spot_id)
    if spot.status != 'O':
        return jsonify({"msg": "Spot is not occupied"}), 400

    # save leaving time in IST (naive datetime)
    reservation.leaving_timestamp = datetime.now(IST).replace(tzinfo=None)

    # Calculate cost
    if reservation.parking_timestamp:
        duration = reservation.leaving_timestamp - reservation.parking_timestamp
        minutes = duration.total_seconds() / 60  # duration in minutes
        hours = minutes / 60
        mins = minutes % 60
        duration_str = f"{hours} hrs {mins} mins" if hours > 0 else f"{mins} mins"
        if hours < 0:
            return jsonify({"msg": "Invalid parking duration"}), 400

        lot = ParkingLot.query.get_or_404(spot.lot_id)

        # precise per-minute billing
        reservation.parking_cost = round((minutes / 60) * lot.price, 2)
    else:
        reservation.parking_cost = 0.0

    spot.status = 'A'
    db.session.commit()

    return jsonify({
        "msg": "Spot released and cost calculated",
        "duration_minutes": minutes,
        "hours": hours,
        "duration": duration_str,
        "parking_cost": reservation.parking_cost
    }), 200

@user_bp.route('/my-statistics', methods=['GET'])
@jwt_required()
@user_required
@cache.cached(timeout=60, query_string=False)
def my_statistics():
    claims = get_jwt()
    user_id = claims.get("sub") or claims.get("id")

    # Totals
    total_reservations = Reservation.query.filter_by(user_id=user_id).count()
    reserved_count = Reservation.query.filter(
        Reservation.user_id == user_id,
        Reservation.parking_timestamp == None
    ).count()
    occupied_count = Reservation.query.filter(
        Reservation.user_id == user_id,
        Reservation.parking_timestamp != None,
        Reservation.leaving_timestamp == None
    ).count()
    released_count = Reservation.query.filter(
        Reservation.user_id == user_id,
        Reservation.leaving_timestamp != None
    ).count()

    total_spent = db.session.query(db.func.sum(Reservation.parking_cost)) \
        .filter(Reservation.user_id == user_id).scalar() or 0

    # Reservations grouped by booking date
    reservations_over_time = db.session.query(
        db.func.date(Reservation.booked_at),
        db.func.count(Reservation.id)
    ).filter(Reservation.user_id == user_id) \
     .group_by(db.func.date(Reservation.booked_at)) \
     .all()

    return jsonify({
        "totals": {
            "reservations": total_reservations,
            "reserved": reserved_count,
            "occupied": occupied_count,
            "released": released_count,
            "spent": total_spent
        },
        "reservations_over_time": [
            {"date": str(date), "count": count}
            for date, count in reservations_over_time
        ]
    }), 200

# Trigger async CSV export
@user_bp.route("/export", methods=["POST"])
@jwt_required()
def export_csv():
    user_id = get_jwt_identity()
    celery = current_app.extensions["celery"]
    task = csv_report.delay(user_id)
    return jsonify({"message": "Export started", "task_id": task.id})


# Check task status (frontend polls this)
@user_bp.route("/export/<task_id>", methods=["GET"])
@jwt_required()
def get_export(task_id):
    celery = current_app.extensions["celery"]
    task = AsyncResult(task_id, app=celery)

    if task.state == "PENDING":
        return jsonify({"status": "pending"})
    elif task.state == "SUCCESS":
        filename = task.result
        filepath = os.path.join("static", filename)
        return send_file(filepath, as_attachment=True, download_name="reservations.csv", max_age=0)
    else:
        return jsonify({"status": task.state})

@user_bp.route('/send_mail')
def send_mail():
    res = send_monthly_reports.delay()
    return {
        "message": res.result
    }