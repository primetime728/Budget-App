from enum import unique
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from sqlalchemy.sql import func

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True)
    password = db.Column(db.Text, nullable=False)

class Ledger(db.Model):
    __tablename__ = "ledger"
    email = db.Column(db.String(345), unique=False)
    id = db.Column('transaction_id', db.Integer, primary_key = True, unique=True)
    category = db.Column(db.String(345), unique=False)
    cost = db.Column(db.Numeric(10,2), unique=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    description = db.Column(db.String(345), unique=False, default="")

    def __repr__(self):
        return f'Email: {self.email}'
    
    def __init__(self, description):
        self.description = description
    
    def format_data(data):
        return {
            "id": data.id,
            "description": data.description
        }