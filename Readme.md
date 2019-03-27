PLC Web App Project
==========

For UFV Capstone project

Requirments
--
- Python 3.6 (NOT 3.7)
- Python-opcua Library
- Python Flask Library
- Python Flask-RQ2

`pip install flask opcua flask_rq2`

How to Run Server
----
1. Install and run "Redis Server"
2. Run `rq worker high normal low default` to launch background worker for main tasks
3. Run `rq worker orders` to launch background worker for Order processing
4. Run App.py


Environment Settings
--
- HMI 192.168.0.211:4870
- Policy:Basic128Rsa15
- MessageSecurityMode: None

App Requirments
---
- Accessible from mobile device
- Set Order
- See success page
- Ideally see update as unit passes through different sections of the process
- If queueing is not implemented in HMI, retrieve HMI orders and use python to track and process queue
