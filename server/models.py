from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(100), nullable=False)

    traffic_logs = db.relationship('TrafficLog', backref='client', lazy=True)

class TrafficLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    bytes_sent = db.Column(db.BigInteger, nullable=False)
    bytes_received = db.Column(db.BigInteger, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
