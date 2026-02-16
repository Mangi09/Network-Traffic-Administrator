from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from models import db, TrafficLog, Client, Alert
from datetime import datetime, timedelta
from functools import wraps

# App Config
app = Flask(__name__)
app.secret_key = "quadnexus_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Restricted Domain Keywords
RESTRICTED_DOMAINS = {
    "youtube": "High",
    "googlevideo": "High",
    "ytimg": "High",
    "1e100.net": "High",
    "instagram": "Medium",
    "facebook": "Medium",
    "netflix": "High",
    "hotstar": "High",
    "discord": "Medium"
}

def check_restricted_domain(domain):
    if not domain:
        return None
    domain = domain.lower()
    for keyword, severity in RESTRICTED_DOMAINS.items():
        if keyword in domain:
            return keyword, severity
    return None

# LOGIN SYSTEM
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# DASHBOARD
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/summary")
@login_required
def summary():

    high = Alert.query.filter_by(severity="High").count()
    medium = Alert.query.filter_by(severity="Medium").count()
    low = Alert.query.filter_by(severity="Low").count()

    total_usage = db.session.query(
        db.func.sum(TrafficLog.bytes_transferred)
    ).scalar() or 0

    recent_alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(5).all()
    recent_logs = TrafficLog.query.order_by(TrafficLog.timestamp.desc()).limit(5).all()

    return jsonify({
        "high": high,
        "medium": medium,
        "low": low,
        "total_usage": total_usage,
        "recent_alerts": [
            {
                "client": a.client.hostname,
                "ip": a.client.ip_address,
                "reason": a.reason,
                "severity": a.severity,
                "time": str(a.timestamp)
            } for a in recent_alerts
        ],
        "recent_logs": [
            {
                "client": l.client.hostname,
                "ip": l.client.ip_address,
                "domain": l.destination_domain,
                "protocol": l.protocol,
                "bytes": l.bytes_transferred,
                "time": str(l.timestamp)
            } for l in recent_logs
        ]
    })

# RECEIVE TRAFFIC
@app.route('/api/traffic', methods=['POST'])
def receive_traffic():
    data = request.json

    hostname = data.get("hostname")
    ip_address = data.get("ip_address")
    mac_address = data.get("mac_address")
    username = data.get("username")
    destination_domain = data.get("destination_domain")
    protocol = data.get("protocol")
    bytes_transferred = data.get("bytes_transferred")

    client = Client.query.filter_by(ip_address=ip_address).first()

    if not client:
        client = Client(
            hostname=hostname,
            ip_address=ip_address,
            mac_address=mac_address,
            username=username
        )
        db.session.add(client)
        db.session.commit()

    log = TrafficLog(
        client_id=client.id,
        destination_domain=destination_domain,
        protocol=protocol,
        bytes_transferred=bytes_transferred
    )

    db.session.add(log)

    # Restricted Domain Alert
    restricted = check_restricted_domain(destination_domain)

    if restricted:
        keyword, severity = restricted
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)

        existing_alert = Alert.query.filter(
            Alert.client_id == client.id,
            Alert.reason.contains(keyword),
            Alert.timestamp >= five_minutes_ago
        ).first()

        if not existing_alert:
            alert = Alert(
                client_id=client.id,
                reason=f"Restricted domain accessed: {destination_domain} ({keyword})",
                severity=severity
            )
            db.session.add(alert)

    # Bandwidth Alert
    if bytes_transferred and bytes_transferred > 10000000:
        alert = Alert(
            client_id=client.id,
            reason="High bandwidth usage detected",
            severity="Medium"
        )
        db.session.add(alert)

    db.session.commit()

    return {"message": "Traffic data saved successfully"}

# VIEW LOGS
@app.route('/view/logs')
@login_required
def view_logs():
    logs = TrafficLog.query.order_by(TrafficLog.timestamp.desc()).all()

    return jsonify({
        "logs": [
            {
                "client": log.client.hostname,
                "ip": log.client.ip_address,
                "domain": log.destination_domain,
                "protocol": log.protocol,
                "bytes": log.bytes_transferred,
                "timestamp": str(log.timestamp)
            } for log in logs
        ]
    })

# VIEW ALERTS
@app.route('/view/alerts')
@login_required
def view_alerts():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).all()

    return jsonify({
        "alerts": [
            {
                "client": alert.client.hostname,
                "ip": alert.client.ip_address,
                "reason": alert.reason,
                "severity": alert.severity,
                "timestamp": str(alert.timestamp)
            } for alert in alerts
        ]
    })

# RUN SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
