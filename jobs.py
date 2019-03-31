from time import sleep

from flask_rq2 import RQ
from opcua import Client
from opcua.ua import VariantType
rq = RQ()


@rq.job
def calculate(x, y):
    print("CACL")
    return x+y

@rq.job
def orderProcess(q):
    print(q)
    print(q["lid"])
    print(q["dye"])
    print(q["table"])

    print("Order Processing")
    client = Client("opc.tcp://192.168.0.211:4870")  # Set OPC-UA Server
    print("STOP")
    client.connect()
    awaitOrder = client.get_node("ns=4;s=M_Awaiting_Order")
    while awaitOrder.get_value() is False:
        print("HMI Not ready")
        sleep(1.0)
    print("HMI is ready. Loading Values")
    M_Lid = client.get_node("ns=4;s=M_Lid_or_No_Lid")
    print("Q" + q["lid"])
    if q["lid"] == "true":
        t = True
    else:
        t = False
    M_Lid.set_value(t)
    print("Lid set" + str(t))
    M_dye = client.get_node("ns=4;s=M_dye_or_No_dye")
    if q["dye"] == "true":
        dyeBool = True
    else:
        dyeBool = False

    M_dye.set_value(dyeBool)
    print("Dye set" + str(dyeBool))
    M_Table = client.get_node("ns=4;s=M_Table_location")
    M_Table.set_value(int(q["table"]), VariantType.Int16)

    print("table set" + q["table"])
    M_process = client.get_node("ns=4;s=M_Send_Order")
    M_process.set_value(True)
    print("process")
    awaitOrder.set_value(False)
    # Now monitor for status int changes
    orderStatusCode = client.get_node()
    job = rq.get

    client.disconnect()
    print("disconnect")

@rq.job
def manualMode(data):
    client = Client("opc.tcp://192.168.0.211:4870")  # Set OPC-UA Server
    if data['runmode'] == "False":
        print("STOP")
        client.connect()
        estop = client.get_node("ns=4;s=M_E_Stop")
        estop.set_value(True)
        sendorder = client.get_node("ns=4;s=M_Send_Order")
        sendorder.set_value(False)
        client.disconnect()
    else:
        print("START")
        client.connect()
        estop = client.get_node("ns=4;s=M_E_Stop")
        estop.set_value(False)
        sendorder = client.get_node("ns=4;s=M_Send_Order")
        sendorder.set_value(True)
        client.disconnect()
    return True

@rq.job
def checkHMI():
    print("CHECK HMI")

