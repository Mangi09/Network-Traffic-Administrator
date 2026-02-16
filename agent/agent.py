import socket
import uuid
import psutil
import requests
import time
import ctypes
import sys
from datetime import datetime

SERVER_URL = "http://127.0.0.1:5000/api/traffic"

seen_connections = set()
last_popup_time = 0
POPUP_COOLDOWN = 30  # seconds

# ==========================================================
# MODE CONFIGURATION
# ==========================================================
# ---- SINGLE PC MODE (Default) ----
# Uses actual hostname and IP of this machine

SINGLE_PC_MODE = False

# ---- MULTI PC MODE (Simulation) ----
# Set SINGLE_PC_MODE = False
# Then run:
# python agent.py 1
# python agent.py 2
# python agent.py 3
# Each number simulates a different PC


# Restricted domain keywords
RESTRICTED_DOMAINS = {
    "youtube": "High",
    "googlevideo": "High",
    "ytimg": "High",
    "1e100.net": "High",
    "instagram": "Medium",
    "facebook": "Medium",
    "netflix": "High",
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


def get_ip():
    return socket.gethostbyname(socket.gethostname())


def get_mac():
    return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                     for elements in range(0, 8*6, 8)][::-1])


def get_protocol_from_port(port):
    if port == 80:
        return "HTTP"
    elif port == 443:
        return "HTTPS"
    elif port == 53:
        return "DNS"
    elif port == 21:
        return "FTP"
    else:
        return "OTHER"


# ==========================================================
# HOSTNAME + IP LOGIC
# ==========================================================
def get_system_identity():

    if SINGLE_PC_MODE:
        # ------------------------------
        # SINGLE PC MODE
        # ------------------------------
        hostname = socket.gethostname()
        ip_address = get_ip()

    else:
        # ------------------------------
        # MULTI PC SIMULATION MODE
        # ------------------------------
        if len(sys.argv) > 1:
            pc_id = sys.argv[1]
        else:
            pc_id = "1"

        hostname = f"PC-{pc_id}"
        ip_address = f"192.168.1.{100 + int(pc_id)}"

    return hostname, ip_address


# ==========================================================
# MAIN LOOP
# ==========================================================
while True:

    hostname, ip_address = get_system_identity()
    mac_address = get_mac()

    connections = psutil.net_connections(kind='inet')

    for conn in connections:
        if conn.raddr:
            remote_ip = conn.raddr.ip
            remote_port = conn.raddr.port

            connection_id = f"{remote_ip}:{remote_port}"
            if connection_id in seen_connections:
                continue

            seen_connections.add(connection_id)

            try:
                domain_name = socket.gethostbyaddr(remote_ip)[0]
            except:
                domain_name = remote_ip

            protocol = get_protocol_from_port(remote_port)

            restricted = check_restricted_domain(domain_name)

            if restricted:
                keyword, severity = restricted
                current_time = time.time()

                if current_time - last_popup_time > POPUP_COOLDOWN:
                    ctypes.windll.user32.MessageBoxW(
                        0,
                        f"⚠ WARNING!\n\nRestricted site detected:\n{keyword}\n\nSeverity: {severity}",
                        "Security Alert",
                        1
                    )
                    last_popup_time = current_time

            data = {
                "hostname": hostname,
                "ip_address": ip_address,
                "mac_address": mac_address,
                "username": "local_user",
                "destination_domain": domain_name,
                "protocol": protocol,
                "bytes_transferred": 5000000
            }

            try:
                requests.post(SERVER_URL, json=data)
                print(f"[{hostname}] Sent data for {domain_name}")
            except Exception as e:
                print("Error sending data:", e)

    time.sleep(10)
