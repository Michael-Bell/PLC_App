import sys
import os
import random
import sys

from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify
from flask_mail import Mail, Message

sys.path.insert(0, "..")
import time

from opcua import Client
from collections import deque
from celery import Celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'flask@example.com'
mail = Mail(app)

dq = deque()
@celery.task
def send_async_email(msg):
    """Background task to send an email with Flask-Mail."""
    with app.app_context():
        mail.send(msg)

@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}

@app.route('/longtask', methods=['POST'])
def longtask():
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@app.route('/')
def menu():
    return render_template('form.html')


@app.route('/manual')  # if http://{url}/manual is requested by a browser
def manMode():
    return render_template('manual.html')  # render this template


@app.route('/manualSubmit', methods=['POST'])  # if form is POSTed to this url
def mresult():
    if request.method == 'POST':
        client = Client("opc.tcp://192.168.0.211:4870")  # Set OPC-UA Server
        result = request.form
        data = request.form.to_dict()
        print(data)
        print(data['runmode'])  # Print selected run options for
        if data['runmode'] == "False":
            print("STOP")
            client.connect()
            estop = client.get_node("ns=3;s=M_E_Stop")
            estop.set_value(True)
            sendorder = client.get_node("ns=3;s=M_Send_Order")
            sendorder.set_value(False)
            client.disconnect()
        else:
            print("START")
            client.connect()
            estop = client.get_node("ns=3;s=M_E_Stop")
            estop.set_value(False)
            sendorder = client.get_node("ns=3;s=M_Send_Order")
            sendorder.set_value(True)
            client.disconnect()
        return render_template("result.html", result=result)

@app.route('/con', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('con.html', email=session.get('email', ''))
    email = request.form['email']
    session['email'] = email

    # send the email
    msg = Message('Hello from Flask',
                  recipients=[request.form['email']])
    msg.body = 'This is a test email sent from a background Celery task.'
    if request.form['submit'] == 'Send':
        # send right away
        send_async_email.delay(msg)
        flash('Sending email to {0}'.format(email))
    else:
        # send in one minute
        send_async_email.apply_async(args=[msg], countdown=60)
        flash('An email will be sent to {0} in one minute'.format(email))

    return redirect(url_for('index'))
@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        result = request.form
        data = request.form.to_dict()
        INTERRUPT_QUEUE.put(data)
        print(data)
        print(dq)
        return render_template("result.html", result=result)


if __name__ == '__main__':
    app.run(debug=True)


def processOrder(dye, lid, table):
    print(str(dye) + str(lid) + str(table))
