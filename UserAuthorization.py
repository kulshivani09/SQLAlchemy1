import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=f"postgresql://{'postgres'}:{'Shiva09'}@{'localhost'}:{'5432'}/{'ecommerce'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["JWT_SECRET_KEY"] = "bgmpsrp0913"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
db=SQLAlchemy(app)
jwt = JWTManager(app)

class Customer(db.Model):
    username=db.Column(db.String(12),primary_key=True,nullable=False)
    password=db.Column(db.String(8),nullable=False)

    def __init__(self,username,password):
        self.username=username
        self.password=password

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

@app.route("/api/InsertUser",methods=['POST'])
@jwt_required()
def insert_user():
    data=request.get_json()
    username=data["username"]
    password = data["password"]
    user1=Customer(username,password)
    db.session.add(user1)
    db.session.commit()
    Customer.query.all()

    return jsonify(user1.as_dict())

@app.route("/api/UpdateUser",methods=['POST'])
@jwt_required()
def update_user():
    data = request.get_json()
    user = Customer.query.get(data['username'])

    if user is not None:
        if 'password' in data.keys():
            user.password = data['password']

        db.session.add(user)
        db.session.commit()
        return jsonify(user.as_dict())
    else:
        return jsonify({"msg":f"{data['username']} does not exist"})

@app.route("/api/DeleteUser",methods=['POST'])
@jwt_required()
def delete_user():
    data = request.get_json()
    user = Customer.query.get(data['username'])
    if not user:
        return jsonify({"message": f"User with ID {data['username']} not found"}), 404
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"User with ID {user} has been deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error while deleting user with ID {user.username}: {str(e)}"}), 500

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

@app.route("/api/Login",methods=['POST'])
def login():
    data=request.get_json()
    username=data['username']
    password=data['password']
    user = Customer.query.get(data['username'])
    if user is not None:
        if user.password == password:
            response = jsonify({"msg": "login successful"})
            access_token = create_access_token(identity=username)
            set_access_cookies(response, access_token)
            return access_token
        else:
            response = jsonify({"msg": "Incorrect Password"})
            return response
    else:
        response = jsonify({"msg": "User not found"})
        return response

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)