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

@app.route("/graphs")
@login_required
def graphs_page():
    return render_template("graphs.html")

# ✅ SUMMARY API
@app.route("/api/summary")
@login_required
def summary():
    yesterday = datetime.utcnow() - timedelta(days=1)

    high = Alert.query.filter(Alert.severity=="High", Alert.timestamp >= yesterday).count()
    medium = Alert.query.filter(Alert.severity=="Medium", Alert.timestamp >= yesterday).count()
    low = Alert.query.filter(Alert.severity=="Low", Alert.timestamp >= yesterday).count()

    daily_usage = db.session.query(
        db.func.sum(TrafficLog.bytes_transferred)
    ).filter(TrafficLog.timestamp >= yesterday).scalar() or 0

    recent_alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(5).all()
    recent_logs = TrafficLog.query.order_by(TrafficLog.timestamp.desc()).limit(5).all()

    return jsonify({
        "high": high,
        "medium": medium,
        "low": low,
        "total_usage": daily_usage,
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

# ✅ ALERT HISTORY
@app.route("/api/alerts/history")
@login_required
def alert_history():
    alerts = Alert.query.join(Client).order_by(Alert.timestamp.desc()).all()

    return jsonify([
        {
            "client": a.client.hostname if a.client else "Unknown",
            "ip": a.client.ip_address if a.client else "N/A",
            "reason": a.reason,
            "severity": a.severity,
            "time": a.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for a in alerts
    ])

# ✅ GRAPH DATA
@app.route("/api/graph-data")
@login_required
def graph_data():
    protocols = db.session.query(TrafficLog.protocol, db.func.count(TrafficLog.id))\
        .group_by(TrafficLog.protocol).all()

    top_clients = db.session.query(Client.hostname, db.func.sum(TrafficLog.bytes_transferred))\
        .join(TrafficLog)\
        .group_by(Client.hostname)\
        .order_by(db.func.sum(TrafficLog.bytes_transferred).desc())\
        .limit(5).all()

    severity_counts = db.session.query(Alert.severity, db.func.count(Alert.id))\
        .group_by(Alert.severity).all()

    recent_traffic = db.session.query(TrafficLog.timestamp, TrafficLog.bytes_transferred)\
        .order_by(TrafficLog.timestamp.desc())\
        .limit(20).all()

    return jsonify({
        "protocols": {p[0]: p[1] for p in protocols},
        "top_clients": {c[0]: c[1] for c in top_clients},
        "severities": {s[0]: s[1] for s in severity_counts},
        "traffic_timeline": [{"time": t[0].strftime("%H:%M:%S"), "bytes": t[1]} for t in reversed(recent_traffic)]
    })

# ✅ MAIN ALERT API (FOR POPUP)
@app.route("/api/get_alerts")
def get_alerts():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(20).all()

    return jsonify([
        {
            "client": a.client.hostname,
            "ip": a.client.ip_address,
            "reason": a.reason,
            "severity": a.severity,
            "time": str(a.timestamp)
        } for a in alerts
    ])

# ✅ RECEIVE TRAFFIC
@app.route('/api/traffic', methods=['POST'])
def receive_traffic():
    data = request.json

    client = Client.query.filter_by(ip_address=data.get("ip_address")).first()

    if not client:
        client = Client(
            hostname=data.get("hostname"),
            ip_address=data.get("ip_address"),
            mac_address=data.get("mac_address"),
            username=data.get("username")
        )
        db.session.add(client)
        db.session.commit()

    log = TrafficLog(
        client_id=client.id,
        destination_domain=data.get("destination_domain"),
        protocol=data.get("protocol"),
        bytes_transferred=data.get("bytes_transferred")
    )

    db.session.add(log)

    restricted = check_restricted_domain(data.get("destination_domain"))

    if restricted:
        keyword, severity = restricted
        alert = Alert(
            client_id=client.id,
            reason=f"Restricted domain accessed: {data.get('destination_domain')} ({keyword})",
            severity=severity
        )
        db.session.add(alert)

    db.session.commit()

    return {"message": "Traffic data saved"}

# ✅ SYSTEM ALERT (USB + GAME)
@app.route('/api/system_alert', methods=['POST'])
def system_alert():
    data = request.json

    client = Client.query.filter_by(ip_address=data.get("ip_address")).first()

    if not client:
        return {"error": "Client not found"}, 404

    if data.get("type") == "game":
        reason = f"Game detected: {data.get('details')}"
    elif data.get("type") == "usb":
        reason = f"USB device inserted: {data.get('details')}"
    else:
        return {"error": "Invalid type"}, 400

    alert = Alert(
        client_id=client.id,
        reason=reason,
        severity="High"
    )

    db.session.add(alert)
    db.session.commit()

    return {"message": "Alert stored"}

# RUN SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)