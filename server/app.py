from flask import Flask, request, jsonify
from models import db, TrafficLog, Client, Alert
from datetime import datetime, timedelta

# =====================================================
# Restricted Domain Keywords
# =====================================================
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

# =====================================================
# Helper Function
# =====================================================
def check_restricted_domain(domain):
    if not domain:
        return None

    domain = domain.lower()

    for keyword, severity in RESTRICTED_DOMAINS.items():
        if keyword in domain:
            return keyword, severity

    return None


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# =====================================================
# RECEIVE TRAFFIC API
# =====================================================
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

    # -------------------------------------------------
    # Check if client exists
    # -------------------------------------------------
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

    # -------------------------------------------------
    # Save traffic log
    # -------------------------------------------------
    log = TrafficLog(
        client_id=client.id,
        destination_domain=destination_domain,
        protocol=protocol,
        bytes_transferred=bytes_transferred
    )

    db.session.add(log)

    # =====================================================
    # RESTRICTED DOMAIN ALERT
    # =====================================================
    restricted = check_restricted_domain(destination_domain)

    if restricted:
        keyword, severity = restricted

        # Prevent duplicate alerts within 5 minutes
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

    # =====================================================
    # BANDWIDTH ALERT
    # =====================================================
    if bytes_transferred and bytes_transferred > 10000000:  # 10MB threshold
        alert = Alert(
            client_id=client.id,
            reason="High bandwidth usage detected",
            severity="Medium"
        )
        db.session.add(alert)

    db.session.commit()

    return {"message": "Traffic data saved successfully"}


# =====================================================
# VIEW LOGS
# =====================================================
@app.route('/view/logs')
def view_logs():
    logs = TrafficLog.query.all()
    result = []

    for log in logs:
        result.append({
            "client": log.client.hostname,
            "ip": log.client.ip_address,
            "domain": log.destination_domain,
            "protocol": log.protocol,
            "bytes": log.bytes_transferred,
            "timestamp": str(log.timestamp)
        })

    return {"logs": result}


# =====================================================
# VIEW ALERTS
# =====================================================
@app.route('/view/alerts')
def view_alerts():
    alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
    result = []

    for alert in alerts:
        result.append({
            "client": alert.client.hostname,
            "ip": alert.client.ip_address,
            "reason": alert.reason,
            "severity": alert.severity,
            "timestamp": str(alert.timestamp)
        })

    return {"alerts": result}


# =====================================================
# RUN SERVER
# =====================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
