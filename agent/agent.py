import socket
import uuid
import psutil
import requests
import time
import ctypes
import sys

# ==========================
# CONFIG
# ==========================
SERVER_URL = "http://10.0.8.43:5000/api/traffic"
SYSTEM_ALERT_URL = "http://10.0.8.43:5000/api/system_alert"

seen_connections = set()
last_popup_time = 0
POPUP_COOLDOWN = 30

SINGLE_PC_MODE = False

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

# ==========================
# FUNCTIONS
# ==========================

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
    return "OTHER"


def get_system_identity():
    if SINGLE_PC_MODE:
        return socket.gethostname(), get_ip()
    else:
        pc_id = sys.argv[1] if len(sys.argv) > 1 else "1"
        return f"PC-{pc_id}", f"192.168.1.{100 + int(pc_id)}"


# 🎮 GAME DETECTION (no external library)
def check_games():
    games = []
    GAME_KEYWORDS = ["chess", "solitaire", "freecell", "mahjong", "minesweeper"]

    for process in psutil.process_iter(['name', 'cmdline']):
        try:
            name = process.info['name'] or ""
            cmd = " ".join(process.info['cmdline']) if process.info['cmdline'] else ""

            text = (name + " " + cmd).lower()

            for keyword in GAME_KEYWORDS:
                if keyword in text:
                    games.append(name)
                    break

        except:
            continue

    return list(set(games))


# 🔌 USB DETECTION
def check_usb():
    devices = []
    for part in psutil.disk_partitions():
        if 'removable' in part.opts.lower():
            devices.append(part.device)
    return devices


# ==========================
# STATE MEMORY
# ==========================
previous_games = set()
previous_usb = set()

# ==========================
# MAIN LOOP
# ==========================
while True:

    hostname, ip_address = get_system_identity()
    mac_address = get_mac()

    # ======================
    # NETWORK MONITORING
    # ======================
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
                        f"⚠ WARNING!\n\nRestricted site:\n{keyword}\nSeverity: {severity}",
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

    # ======================
    # GAME DETECTION
    # ======================
    current_games = set(check_games())
    new_games = current_games - previous_games

    for game in new_games:
        try:
            requests.post(SYSTEM_ALERT_URL, json={
                "ip_address": ip_address,
                "type": "game",
                "details": game
            })
            print(f"[{hostname}] 🎮 Game detected: {game}")
        except Exception as e:
            print("Error sending game alert:", e)

    previous_games = current_games

    # ======================
    # USB DETECTION
    # ======================
    current_usb = set(check_usb())
    new_usb = current_usb - previous_usb

    for usb in new_usb:
        try:
            requests.post(SYSTEM_ALERT_URL, json={
                "ip_address": ip_address,
                "type": "usb",
                "details": usb
            })
            print(f"[{hostname}] 🔌 USB detected: {usb}")
        except Exception as e:
            print("Error sending USB alert:", e)

    previous_usb = current_usb

    time.sleep(10)