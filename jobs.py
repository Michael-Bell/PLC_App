from time import sleep

from flask_rq2 import RQ
from opcua import Client
from opcua.ua import VariantType
from rq import get_current_job

rq = RQ()


@rq.job
def calculate(x, y):
    print("CACL")
    return x + y


@rq.job
def DyeOrder(q):
    awaitOrder = "ns=4;s=M_DYE_Awaiting_Order"
    lidNoLid = "ns=4;s=M_DYE_Lid_or_No_Lid"
    tableLoc = "ns=4;s=M_DYE_Table_location"
    MProc = "ns=4;s=M_Send_Order"
    updateCounter = "ns=4;s=M_DYE_STAT_COUNTER"
    updateInt = "ns=4;s=M_DYE_STAT_INT"
    orderProcess(True, awaitOrder, lidNoLid, tableLoc, MProc, updateCounter, updateInt, q)


@rq.job
def NoDyeOrder(q):
    awaitOrder = "ns=4;s=NDYE_Awaiting_Order"
    lidNoLid = "ns=4;s=NDYE_Lid_or_No_Lid"
    tableLoc = "ns=4;s=NDYE_Table_location"
    MProc = "ns=4;s=NDYE_Send_order"
    updateCounter = "ns=4;s=NDYE_STAT_COUNTER"
    updateInt = "ns=4;s=NDYE_STAT_INT"
    orderProcess(False, awaitOrder, lidNoLid, tableLoc, MProc, updateCounter,updateInt, q)


def orderProcess(queueType, awaitOrder, lidNoLid, tableLoc, MProc, updateCounter, updateInt, q):
    orderJob = get_current_job()
    orderJob.meta['lid'] = q["lid"]
    orderJob.meta['progress'] = 0
    orderJob.save_meta()
    print(orderJob)
    print(orderJob.meta)
    print(orderJob.kwargs)
    kukaDoneID = "ns=4;s=DI_KUKA_SIGNAL_DONE"
    kukaRunningID = "ns=4;s=DI_KUKA_SIGNAL_START"
    kukaWaitingID = "ns=4;s=DI_KUKA_SIGNAL_WAITING_ORDER"
    selectedQueueID = "ns=4;s=SELECTED_QUEUE"
    # print(q)
    # print(q["lid"])
    # print(q["dye"])
    # print(q["table"])
    isOPCAvailable = False
    try:
        # print("Order Processing")
        client = Client("opc.tcp://192.168.0.211:4870")  # Set OPC-UA Server
        # print("STOP")
        client.connect()
        awaitOrder = client.get_node(awaitOrder)
        while awaitOrder.get_value() is False:
            # print("HMI Not ready")
            sleep(1.0)
        # print("HMI is ready. Loading Values")
        M_Lid = client.get_node(lidNoLid)
        # print("Q" + q["lid"])
        if q["lid"] == "true":
            t = True
        else:
            t = False
        M_Lid.set_value(t)
        # print("Dye set" + str(dyeBool))
        M_Table = client.get_node(tableLoc)
        M_Table.set_value(int(q["table"]), VariantType.Int16)

        # print("table set" + q["table"])
        M_process = client.get_node(MProc)
        M_process.set_value(True)
        # print("process")
        awaitOrder.set_value(False)
        isOPCAvailable = True
    except OSError:
        print("OPC Server Unavailable")

    # Now monitor for status int changes
    # orderStatusCode = client.get_node()
    orderJob = get_current_job()
    orderJob.meta['progress'] = 0
    orderJob.save_meta()
    progressInt = 0
    if isOPCAvailable is False:
        asdf = 0
        while asdf < 10:
            orderJob.meta['progress'] = asdf
            # print(orderJob)
            # print(asdf)
            orderJob.save_meta()
            sleep(2)
            asdf = asdf + 1
        orderJob.meta['progress'] = "Success"
        orderJob.save_meta()
    else:
        while orderJob.meta['progress'] != 11:
            countVal = client.get_node(updateCounter).get_value()
            intVal = client.get_node(updateInt).get_value()
            kukaQueue = client.get_node(selectedQueueID).get_value()
            kukaRun = client.get_node(kukaRunningID).get_value()
            kukaDone = client.get_node(kukaDoneID).get_value()

            if ((((kukaQueue=="True") & (queueType==True)) or ((kukaQueue=="False") & (queueType==False))) & ((kukaRun=="True") or (kukaDone == "True"))): # IF The selected queue and working queue match, AND the kuka is in run sequence
                orderJob.meta['progress'] = intVal
            else:
                orderJob.meta['progress'] = countVal
            orderJob.save_meta()
            sleep(1)




    try:
        client.disconnect()
    except (OSError, AttributeError) as e:
        print("OPC Unavailable")
    print("disconnect")


@rq.job
def manualMode(data):
    client = Client("opc.tcp://192.168.0.211:4870")  # Set OPC-UA Server
    if data['runmode'] == "False":
        # print("STOP")
        client.connect()
        estop = client.get_node("ns=4;s=M_E_Stop")
        estop.set_value(True)
        sendorder = client.get_node("ns=4;s=M_Send_Order")
        sendorder.set_value(False)
        client.disconnect()
    else:
        # print("START")
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


@rq.job
def updateJob():
    print("CHECK HMI")
