from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Missing name, email, or password!"}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Email already registered!"}), 409

    new_user = User(
        name=data['name'],
        email=data['email'],
        role='user',
        user_pincode=data.get('user_pincode'),
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Registration successfull! You can log in now!"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(data)
    user = User.query.filter_by(email=data.get('email')).first()
    print(user)
    if not user:
        return jsonify({"msg": "User not found!"}), 401
    if user.check_password(data.get('password')):
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"name": user.name,"email": user.email, "role": user.role, "user_pincode": user.user_pincode}
        )
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Invalid email or password!"}), 401