from flask import Blueprint, request, jsonify #type: ignore
from flask_jwt_extended import jwt_required, get_jwt #type: ignore
from models import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timezone
from jobs.reminders import generate_msg
from caching import cache

admin_bp = Blueprint('admin', __name__)

# Helper to check admin role
def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"msg": "Admins only!"}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

# Create a new Parking Lot
@admin_bp.route('/create-new-lot', methods=['POST'])
@jwt_required()
@admin_required
def create_new_lot():
    data = request.get_json()
    
    if not data.get('city') or not data.get('address') or not data.get('pincode') or not data.get('price') or not data.get('number_of_spots'):
        return jsonify({"msg": "Missing required fields!"}), 400
    
    # There cannot be a lot with the same address and pincode
    existing_lot = ParkingLot.query.filter_by(address=data['address'], pincode=data['pincode']).first()
    if existing_lot:
        return jsonify({"msg": "Parking lot with this address and pincode already exists!"}), 409

    new_lot = ParkingLot(
        city=data['city'],
        address=data['address'],
        pincode=data['pincode'],
        price=data['price'],
        number_of_spots=data['number_of_spots']
    )
    
    for _ in range(data['number_of_spots']):
        new_lot.spots.append(ParkingSpot(status='A'))
    
    db.session.add(new_lot)
    db.session.commit() 
    non_admin_users = User.query.filter(User.role != 'admin').all()
    for user in non_admin_users:
        res=generate_msg.delay(user.name, new_lot.city)
    return jsonify({"msg": "Parking lot created"}), 201

# Edit an existing Parking Lot
@admin_bp.route('/edit-lot/<int:lot_id>', methods=['PUT'])
@jwt_required()
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    data = request.get_json()

    new_count = data.get('number_of_spots')
    current_count = lot.number_of_spots
    
    # Count current available spots
    available_spots = [spot for spot in lot.spots if spot.status == 'A']
    
    lot.city = data['city']
    lot.address = data['address']
    lot.pincode = data['pincode']
    lot.price = data['price']

    # Spot addition
    if new_count > current_count:
        for _ in range(new_count - current_count):
            lot.spots.append(ParkingSpot(status='A'))

    # Spot deletion
    elif new_count < current_count:
        delta = current_count - new_count
        if len(available_spots) < delta:
            return jsonify({"msg": f"Cannot remove {delta} spots. Only {len(available_spots)} available to delete."}), 400

        # Sort available spots in descending ID order (optional, to delete latest)
        to_remove = sorted(available_spots, key=lambda s: s.id, reverse=True)[:delta]
        for spot in to_remove:
            db.session.delete(spot)

    lot.number_of_spots = new_count
    
    db.session.commit()
    return jsonify({"msg": "Lot updated"}), 200

# Delete a Parking Lot
@admin_bp.route('/delete-lot/<int:lot_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    # Check if any spot is not available
    occupied_or_reserved = [spot for spot in lot.spots if spot.status != 'A']
    if occupied_or_reserved:
        return jsonify({"msg": "Cannot delete lot. Some spots are reserved or occupied."}), 400

    # Delete associated spots
    for spot in lot.spots:
        db.session.delete(spot)

    # Delete the lot itself
    db.session.delete(lot)
    db.session.commit()

    return jsonify({"msg": f"Lot #{lot_id} deleted successfully."}), 200

#Get one parking lot by ID
@admin_bp.route('/get-lot/<int:lot_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    data = {
        "id": lot.id,
        "city": lot.city,
        "address": lot.address,
        "pincode": lot.pincode,
        "price": lot.price,
        "total_spots": lot.number_of_spots,
        "available_spots": len([s for s in lot.spots if s.status == 'A']),
        "reserved_spots": len([s for s in lot.spots if s.status == 'R']),
        "date_created": lot.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        "spots": []
    }

    for spot in lot.spots:
        reservation = Reservation.query.filter_by(spot_id=spot.id).order_by(Reservation.booked_at.desc()).first()
        user_info = None
        if reservation and reservation.leaving_timestamp is None:
            user = User.query.get(reservation.user_id)
            if user:
                user_info = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "user_pincode": user.user_pincode,
                    "booked_at": reservation.booked_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "parking_timestamp": reservation.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S') if reservation.parking_timestamp else None,
                    "leaving_timestamp": reservation.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if reservation.leaving_timestamp else None,
                    "parking_cost": reservation.parking_cost if reservation.parking_cost else None
                }

        data["spots"].append({
            "id": spot.id,
            "status": spot.status,
            "user": user_info
        })

    return jsonify(data), 200

# Get all Parking Lots
@admin_bp.route('/get-all-lots', methods=['GET'])
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

# Get all users
@admin_bp.route('/get-all-users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    users = User.query.filter(User.role != 'admin').all()
    data = []
    for user in users:
        data.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "user_pincode": user.user_pincode,
            "date_joined": user.date_created.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(data), 200

# Get user reservations by user ID
@admin_bp.route('/get-user-reservations/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
@cache.cached(timeout=60, query_string=True)
def get_user_reservations(user_id):
    user = User.query.get_or_404(user_id)
    reservations = Reservation.query.filter_by(user_id=user.id).all()
    # print(f"Reservations for user {user_id}: {reservations}")
    data = []
    for res in reservations:
        spot = ParkingSpot.query.get(res.spot_id)
        lot = ParkingLot.query.get(spot.lot_id) if spot else None
        data.append({
            "reservation_id": res.id,
            "user_name": user.name,
            "lot_id": lot.id if lot else None,
            "lot_city": lot.city if lot else None,
            "lot_address": lot.address if lot else None,
            "lot_pincode": lot.pincode if lot else None,
            "lot_price": lot.price if lot else None,
            "spot_id": spot.id if spot else None,
            "status": spot.status if spot else None,
            "booked_at": res.booked_at.strftime('%Y-%m-%d %H:%M:%S'),
            "vehicle_number": res.vehicle_number,
            "parking_timestamp": res.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.parking_timestamp else None,
            "leaving_timestamp": res.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.leaving_timestamp else None,
            "parking_cost": res.parking_cost if res.parking_cost else None
        })
    return jsonify(data), 200

# Get statistics for admin 
@admin_bp.route('/statistics', methods=['GET'])
@jwt_required()
@admin_required
@cache.cached(timeout=60, query_string=False)
def statistics():
    total_users = User.query.filter_by(role='user').count()
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    reserved_spots = ParkingSpot.query.filter_by(status='R').count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()

    total_reservations = Reservation.query.count()
    total_revenue = db.session.query(db.func.sum(Reservation.parking_cost)).scalar() or 0

    # Reservations by lot
    reservations_by_lot = db.session.query(
        ParkingLot.city,
        ParkingLot.address,
        db.func.count(Reservation.id)
    ).join(ParkingSpot, ParkingLot.id == ParkingSpot.lot_id) \
     .join(Reservation, ParkingSpot.id == Reservation.spot_id) \
     .group_by(ParkingLot.id).all()

    # Reservations over time (grouped by day)
    reservations_over_time = db.session.query(
        db.func.date(Reservation.booked_at),
        db.func.count(Reservation.id)
    ).group_by(db.func.date(Reservation.booked_at)).all()

    return jsonify({
        "totals": {
            "users": total_users,
            "lots": total_lots,
            "spots": total_spots,
            "available_spots": available_spots,
            "reserved_spots": reserved_spots,
            "occupied_spots": occupied_spots,
            "reservations": total_reservations,
            "revenue": total_revenue
        },
        "reservations_by_lot": [
            {"lot": f"{city}, {address}", "count": count} for city, address, count in reservations_by_lot
        ],
        "reservations_over_time": [
            {"date": str(date), "count": count} for date, count in reservations_over_time
        ]
    }), 200
