from datetime import datetime
from ipaddress import ip_address
from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_session import Session
from config import ApplicationConfig
from models import db, User, Ledger
import table_data
import configparser

app = Flask(__name__)
app.config.from_object(ApplicationConfig)

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
server_session = Session(app)
db.init_app(app)

config = configparser.ConfigParser()
config.read_file(open(r'server_config.txt'))
ip_address = config.get('Server Config', 'ip_address')

with app.app_context():
    db.create_all()

@app.route("/@me")
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    print ("1# = " + str(session.get("user_id")))
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        "id": user.id,
        "email": user.email
    }) 

@app.route("/register", methods=["POST"])
def register_user():
    email = request.json["email"]
    password = request.json["password"]

    user_exists = User.query.filter_by(email=email).first() is not None

    # If user already exists (409 conflict)
    if user_exists:
        return jsonify({"error": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id
    return jsonify({
        "id": new_user.id,
        "email": new_user.email
    })

@app.route("/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401
    
    session["user_id"] = user.id
    print ("2! =" + session.get("user_id"))
    return jsonify({
        "id": user.id,
        "email": user.email
    })

@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return "200"

@app.route('/')
def testdb():
    if db.session.query('1').from_statement('SELECT 1').all():
        return 'It works.'
    else:
        return 'Something is broken.'

# create an event
@app.route('/ledger', methods = ['POST'])
def create_event():
    print ("3# = " + str(session.get("user_id")))
    print(request.json['user_id'])
    userID = request.json['user_id']
    description = request.json['description']
    event = Ledger(userID, description)
    db.session.add(event)
    db.session.commit()

    return format_event(event)

# get all events based on user logged in
@app.route('/ledger', methods = ['GET'])
def get_ledger():
    #print ("^ =" + str(session))
    #userID = request.json['user_id']
    events = Ledger.query.order_by(Ledger.id.asc()).all()
    event_list = []
    for event in events:
        event_list.append(format_event(event))
    return {'event': event_list}

# get an event
@app.route('/ledger/<id>', methods = ['GET'])
def get_event(id):
    event = Ledger.query.filter_by(id=id).one()
    formatted_event = format_event(event)
    return {'event': formatted_event}

# delete an event
@app.route('/ledger/<id>', methods = ['DELETE'])
def delete_event(id):
    event = Ledger.query.filter_by(id=id).one()
    db.session.delete(event)
    db.session.commit()
    return f'Event (id: {id}) deleted!'

# edit an event
@app.route('/ledger/<id>', methods = ['PUT'])
def update_event(id):
    event = Ledger.query.filter_by(id=id)
    description = request.json['description']
    event.update(dict(description = description, created_at = datetime.now()))
    db.session.commit()
    return {'event': format_event(event.one())}

def format_event(event):
    return {
        "id": event.id,
        "user_id": event.user_id,
        "cost": event.cost,
        "created_at": event.created_at,
        "description": event.description
    }

if __name__ == "__main__":
    app.run(host=ip_address,debug=True)