import psutil
import socket
import requests
import time
import json

# SERVER API URL (change IP if needed)
SERVER_URL = "http://127.0.0.1:5000/api/traffic"

def get_system_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return hostname, ip_address

def get_network_usage():
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_received = net_io.bytes_recv
    return bytes_sent, bytes_received

def send_data_to_server(data):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            SERVER_URL,
            data=json.dumps(data),
            headers=headers,
            timeout=5
        )
        print("Data sent:", response.status_code)
    except Exception as e:
        print("Error sending data:", e)

def main():
    print("Client Agent Started...")
    
    hostname, ip_address = get_system_info()

    while True:
        bytes_sent, bytes_received = get_network_usage()

        data = {
            "hostname": hostname,
            "ip_address": ip_address,
            "bytes_sent": bytes_sent,
            "bytes_received": bytes_received
        }

        send_data_to_server(data)

        time.sleep(10)  # send data every 10 seconds

if __name__ == "__main__":
    main()
