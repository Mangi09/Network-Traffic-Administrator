from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Clients Table
class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False, unique=True)
    mac_address = db.Column(db.String(50))
    username = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    traffic_logs = db.relationship("TrafficLog", backref="client", lazy=True)
    alerts = db.relationship("Alert", backref="client", lazy=True)

# Traffic Logs Table
class TrafficLog(db.Model):
    __tablename__ = "traffic_logs"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),   
        nullable=False
    )

    destination_domain = db.Column(db.String(200))
    protocol = db.Column(db.String(20))
    bytes_transferred = db.Column(db.BigInteger)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Alerts Table
class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(
        db.Integer,
        db.ForeignKey("clients.id"),   
        nullable=False
    )

    reason = db.Column(db.String(255))
    severity = db.Column(db.String(50))

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
