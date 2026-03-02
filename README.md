# QuadNexus  
Intelligent LAN Security Monitoring System

QuadNexus is a lightweight, agent-based LAN security monitoring system that provides real-time visibility into internal network activity. It detects restricted domain access, monitors bandwidth usage, and generates categorized security alerts through a centralized web dashboard.

Built for proactive network intelligence in educational institutions, labs, and small organizations.

## Problem Statement

Small and medium-scale institutions often lack enterprise-grade internal network monitoring systems. As a result:

- Unauthorized streaming and bandwidth abuse go undetected  
- No real-time alerts for restricted domain access  
- IT teams react only after issues escalate  
- No centralized visibility across multiple LAN devices  

QuadNexus addresses these challenges with a scalable and lightweight monitoring architecture.

## Solution Overview

QuadNexus introduces:

- Agent-based network monitoring  
- Centralized Flask backend  
- Real-time alert classification  
- Multi-device tracking  
- Bandwidth anomaly detection  
- Secure admin dashboard  

The system enables administrators to proactively monitor internal traffic and respond instantly to suspicious activity.

## System Architecture
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/3986a5ee-bb1e-41aa-ab1d-6c7adcf39cd1" />




## Core Components

### Agent Layer (Client-Side Monitoring)

Runs on each LAN device and performs:

- Network connection monitoring using psutil  
- Reverse DNS resolution  
- Restricted domain detection  
- Protocol classification  
- Periodic data transmission to server  

Supports:
- Single PC mode  
- Multi-PC simulation mode  

### Backend Server (Flask API)

Responsible for:

- Receiving traffic logs  
- Creating client entries dynamically  
- Detecting restricted domain access  
- Bandwidth threshold analysis  
- Generating severity-based alerts  
- Preventing duplicate alerts (5-minute window)  
- Providing dashboard APIs  

### Database (SQLite)

Tables used:

Clients  
- Hostname  
- IP address  
- MAC address  
- Username  

Traffic Logs  
- Destination domain  
- Protocol  
- Bytes transferred  
- Timestamp  

Alerts  
- Severity (High / Medium / Low)  
- Reason  
- Timestamp  

### Dashboard (Frontend)

Built using:

- Bootstrap 5  
- Custom CSS  
- Chart.js for data visualization  

Features:

- Alert severity summary cards  
- Traffic trend graph  
- Alert distribution chart  
- Recent alerts table  
- Connected devices list  
- Auto-refresh every 5 seconds  
- Secure login system  

## Alert Detection Logic

### Restricted Domain Monitoring

Predefined domains categorized as:

High Severity:
- YouTube  
- Netflix  
- GoogleVideo  
- 1e100.net  

Medium Severity:
- Instagram  
- Facebook  
- Discord  

Alerts are triggered when domain keywords are detected.

### Bandwidth Anomaly Detection

If:
bytes_transferred > 10MB


The system generates a Medium severity alert.

### Duplicate Alert Prevention

The system prevents repeated alerts for the same client within a 5-minute window.

## Authentication

- Admin login system  
- Session-based authentication  
- Protected routes  
- Logout functionality  

Default Credentials:
- Username: admin
- Password: admin123
  
<img width="1920" height="886" alt="image" src="https://github.com/user-attachments/assets/cfa6bf4b-d877-47d7-8b78-effefe1ec526" />



## Multi-PC Simulation

QuadNexus supports simulation of multiple LAN devices.

Single PC Mode:

```bash 
python agent.py
```

Multi-PC Mode:

Set in agent.py: SINGLE_PC_MODE = False

Then run:

```bash 
python agent.py 1
```

```bash
python agent.py 2
```

```bash 
python agent.py 3
```


Each instance simulates a unique LAN device.
<img width="1920" height="891" alt="image" src="https://github.com/user-attachments/assets/9930c56a-1df9-45b8-bd3a-204a45a96341" />


<img width="249" height="243" alt="image" src="https://github.com/user-attachments/assets/662f860b-42b1-44d1-b124-af70fc5f0dbb" />


<img width="1920" height="888" alt="image" src="https://github.com/user-attachments/assets/91406c59-c846-4e75-9c80-1b3f195dd9ce" />




## Installation Guide

Clone Repository:

```bash
https://github.com/Mangi09/Network-Traffic-Administrator
```

```bash
cd QuadNexus
```


Create Virtual Environment (Recommended)

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```


Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```


Install Dependencies:
```bash
pip install -r requirements.txt
```


## Running the Application

Start Backend Server:
```bash
python server/app.py
```


Start Agent:
```bash
python agent/agent.py
```


## Demo Flow

1. Start backend server  
2. Start 2–3 simulated agents  
3. Access a restricted site (e.g., YouTube)  
4. Alert popup is triggered  
5. Dashboard updates within 5 seconds  
6. Severity counter increases  

## Technologies Used

- Python  
- Flask  
- Flask-SQLAlchemy  
- SQLite  
- Bootstrap 5  
- Chart.js  
- psutil  
- requests  

## Academic and Technical Value

This project demonstrates:

- Agent-based distributed monitoring  
- Client-server architecture  
- REST API design  
- Real-time dashboard analytics  
- Alert classification systems  
- Network traffic analysis  
- Cybersecurity domain filtering  

## Future Enhancements

- WebSocket real-time updates  
- Email or SMS notifications  
- SNMP protocol integration  
- Machine learning anomaly detection  
- Role-based admin system  
- Cloud deployment  
- Docker containerization  

## Team QuadNexus

- Vibha  
- Dwithi  
- Arohi  
- Anjali  

## License

This project is developed for academic and hackathon purposes.
