from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=f"postgresql://{'postgres'}:{'Shiva09'}@{'localhost'}:{'5432'}/{'FlaskAPI1'}"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Shiva09@localhost:5430/FlaskAPI1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)


class Customer(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))
    email=db.Column(db.String(100),unique=True)

    def __init__(self,id,name,email):
        self.id=id
        self.name=name
        self.email=email

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

@app.route("/api/InsertUser",methods=['POST'])
def insert_user():
    data=request.get_json()
    id=data["id"]
    name = data["name"]
    email = data["email"]
    user1=Customer(id,name,email)
    db.session.add(user1)
    db.session.commit()
    user_new=Customer.query.all()
    print(type(user_new))
    print(user_new)

    return {"user": id, "message": f"user {name} inserted"}, 201

@app.route("/api/UpdateUser",methods=['POST'])
def update_user():
    data = request.get_json()
    user = Customer.query.get(data['id'])

    if user is not None:
        if 'name' in data.keys():
            user.name = data['name']

        '''if ('last_name' in data.keys()):
            user.last_name = data['last_name']
        if ('phone_no' in data.keys()):
            user.phone_no = data['phone_no']
        if ('is_admin' in data.keys()):
            user.is_admin = data['is_admin']'''

        db.session.add(user)
        db.session.commit()
        return jsonify(user.as_dict())


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)