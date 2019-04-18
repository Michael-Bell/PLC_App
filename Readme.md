PLC Web App Project
==========

For UFV Capstone project

Arduino Code
----
[aott33/Gripper_control](https://github.com/aott33/Gripper_control)


Requirments
--
- Python 3.6 (NOT 3.7)
- Python-opcua Library
- Python Flask Library
- Python Flask-RQ2

`pip install flask opcua flask_rq2`

How to Run Server
----
1. Install Docker and docker-compose
2. Run `docker-compose up`


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
