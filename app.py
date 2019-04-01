from collections import deque
from time import sleep

import redis
from flask import Flask, request, render_template, jsonify
from flask_rq2 import RQ
from rq import Queue, Connection

app = Flask(__name__)
app.config['RQ_REDIS_URL'] = 'redis://rq-server:6379/0'

rq = RQ(app)

dq = deque()


@app.route('/add/<int:x>/<int:y>')
def add(x, y):
    from jobs import calculate
    job = calculate.queue(x, y)
    sleep(2.0)
    return str(job.result)


@app.route('/')
def menu():
    return render_template('form.html')


@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        data = request.form.to_dict()
        print(data)
        from jobs import orderProcess
        job = orderProcess.queue(data, queue='orders')
        returnData = [job.id, request.form]
        print(returnData)
        # return render_template("result.html", result=result1, id=job.id)
        return jsonify(returnData), 202


@app.route('/tasks/<task_id>', methods=['GET'])
def get_status(task_id):
    with Connection(redis.from_url(app.config['RQ_REDIS_URL'])):
        print("getting status" + task_id)
        q = Queue('orders')
        task = q.fetch_job(task_id)
        status = "error"
        try:
            if task.get_status() == "queued":
                status = "queued"
            elif task.meta == {}:
                status = "starting"
            elif task.meta['progress'] <= 1:
                status = "On Conveyor"
            elif task.meta['progress'] <= 3:
                status = "Filling Bottle"
            elif task.meta['progress'] <= 6:
                status = "On Conveyor"
            elif (task.meta['progress'] <= 8 and task.meta['lid'] == "true"):
                status = "Lid Station"
            elif task.meta['progress'] <= 9:
                status = "Kuka arm to table"
            else:
                status = "def"
        except TypeError:
            if task.meta['progress'] == "Success":
                status = "Success"
        try:
            if 0 <= task.meta['progress'] <= 10:
                task_percent = task.meta['progress'] * 10
        except (TypeError, KeyError):
            if (task.meta == {} or task.get_status() == 'queued'):
                task_percent = 0
            else:
                task_percent = 100
        print(task.meta)
        print(task)
        print("RESULT" + str(task.result))
    if task:
        response_object = {
            'status': 'success',
            'data': {
                'task_id': task.get_id(),
                'task_status': status,
                'task_result': task.result,
                'task_percent': task_percent,
            }
        }
    else:
        response_object = {'status': 'error'}
    return jsonify(response_object)


from jobs import rq

@app.route('/manual')  # if http://{url}/manual is requested by a browser
def manMode():
    return render_template('manual.html')  # render this template


@app.route('/manualSubmit', methods=['POST'])  # if form is POSTed to this url
def mresult():
    if request.method == 'POST':
        result = request.form
        data = request.form.to_dict()
        print(data)
        print(data['runmode'])  # Print selected run options for
        from jobs import manualMode
        job = manualMode.queue(data)
        return render_template("result.html", result=result)



rq.init_app(app)
#from jobs import checkHMI

#checkHMI.cron('* * * * *', 'Check-HMI', 1, 2)

if __name__ == '__main__':
    from jobs import rq

    print("HI")
    rq.init_app(app)
    app.run(host='0.0.0.0')
