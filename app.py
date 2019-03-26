from flask import Flask, render_template, request
import sys
sys.path.insert(0, "..")
import time

from opcua import Client
from opcua import ua

app = Flask(__name__)


@app.route('/')
def menu():
    return render_template('form.html')


@app.route('/manual')
def manMode():
    return render_template('manual.html')


@app.route('/manualSubmit', methods=['POST'])
def mresult():
    if request.method == 'POST':
        client = Client("opc.tcp://192.168.0.211:4870")
        result = request.form
        data = request.form.to_dict()
        print(data)
        print(data['runmode'])
        if data['runmode'] == "False":
            print("STOP")
            client.connect()
            estop = client.get_node("ns=3;s=M_E_Stop")
            estop.set_value(True)
            sendorder= client.get_node("ns=3;s=M_Send_Order")
            sendorder.set_value(False)
            client.disconnect()
        else:
            print("START")
            client.connect()
            estop = client.get_node("ns=3;s=M_E_Stop")
            estop.set_value(False)
            sendorder =client.get_node("ns=3;s=M_Send_Order")
            sendorder.set_value(True)
            client.disconnect()
        return render_template("result.html", result=result)


@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        result = request.form
        data = request.form.to_dict()
        print(data)
        processOrder(request.form.get['dye'], request.form.get['lid'], request.form.get['table'])
        return render_template("result.html", result=result)


if __name__ == '__main__':
    app.run(debug=True)


def processOrder(dye, lid, table):
    print(str(dye) + str(lid) + str(table))
