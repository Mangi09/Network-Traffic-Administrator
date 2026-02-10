from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/traffic", methods=["POST"])
def receive_traffic():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data received"}), 400

    print("Received data from client:")
    print(data)

    return jsonify({"message": "Data received successfully"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
