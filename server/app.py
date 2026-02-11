from flask import Flask, request, jsonify
from models import db, TrafficLog, Client

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
@app.route('/api/traffic', methods=['POST'])
def receive_traffic():
    data = request.json

    hostname = data.get("hostname")
    ip_address = data.get("ip_address")
    bytes_sent = data.get("bytes_sent")
    bytes_received = data.get("bytes_received")

    # Check if client exists
    client = Client.query.filter_by(ip_address=ip_address).first()

    if not client:
        client = Client(hostname=hostname, ip_address=ip_address)
        db.session.add(client)
        db.session.commit()

    # Create traffic log
    log = TrafficLog(
        client_id=client.id,
        bytes_sent=bytes_sent,
        bytes_received=bytes_received
    )

    db.session.add(log)
    db.session.commit()

    return {"message": "Data saved successfully"}


@app.route('/view')
def view_data():
    logs = TrafficLog.query.all()
    result = []

    for log in logs:
        result.append({
            "client_id": log.client_id,
            "bytes_sent": log.bytes_sent,
            "bytes_received": log.bytes_received,
            "timestamp": str(log.timestamp)
        })

    return {"data": result}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
