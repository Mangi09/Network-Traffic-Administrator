import socket
import uuid
import psutil
import requests
import time

SERVER_URL = "http://127.0.0.1:5000/api/traffic"


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


while True:
    hostname = socket.gethostname()
    ip_address = get_ip()
    mac_address = get_mac()

    connections = psutil.net_connections(kind='inet')

    for conn in connections:
        if conn.raddr:
            remote_ip = conn.raddr.ip
            try:
                domain_name = socket.gethostbyaddr(remote_ip)[0]
            except:
                domain_name = remote_ip

            remote_port = conn.raddr.port

            protocol = get_protocol_from_port(remote_port)

            bytes_sent = psutil.net_io_counters().bytes_sent
            bytes_recv = psutil.net_io_counters().bytes_recv

            data = {
                "hostname": hostname,
                "ip_address": ip_address,
                "mac_address": mac_address,
                "username": "local_user",
                "destination_domain": domain_name,
                "protocol": protocol,
                "bytes_transferred": bytes_sent + bytes_recv
            }

            try:
                requests.post(SERVER_URL, json=data)
            except:
                pass

    time.sleep(10)
