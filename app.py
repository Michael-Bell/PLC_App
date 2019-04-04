from collections import deque
from time import sleep

import redis
from flask import Flask, request, render_template, jsonify
from flask_rq2 import RQ
from rq import Queue, Connection

app = Flask(__name__)
app.config['RQ_REDIS_URL'] = 'redis://localhost:6379/0'

rq = RQ(app)

dq = deque()
jobQueue=[]
jobDone=[]
jobWork = []
@app.route('/add/<int:x>/<int:y>')
def add(x, y):
    from jobs import calculate
    job = calculate.queue(x, y)
    sleep(2.0)
    return str(job.result)


@app.route('/')
def menu():
    return render_template('form.html')

@app.route('/screen')
def screen():
    return render_template('screen.html')

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        data = request.form.to_dict()
        #print(data)
        from jobs import orderProcess
        job = orderProcess.queue(data, queue='orders')
        returnData = [job.id, request.form]
        jobQueue.append(job.id)
        #print(returnData)
        # return render_template("result.html", result=result1, id=job.id)
        return jsonify(returnData), 202

@app.route('/updatescreen',methods=['GET'])
def updateScreen():
    print(jobQueue)
    response_object = {
        'status': 'success',
        'data': {"q":jobQueue,
                 "w": jobWork,
                 "d": jobDone}
    }

    return jsonify(response_object)

@app.route('/tasks/<task_id>', methods=['GET'])
def get_status(task_id):
    with Connection(redis.from_url(app.config['RQ_REDIS_URL'])):
        q = Queue('orders')
        task = q.fetch_job(task_id)
        status = "error"
        task_percent=0
        try:
            if (task.meta=={'lid': 'true'} or task.meta=={'lid': 'false'}):
                task_percent = "Next in line"
            if 0 <= task.meta['progress'] <= 10:
                task_percent = task.meta['progress'] * 10
        except (TypeError):
            if ( task.get_status() == 'queued'):
                task_percent = 0
            else:
                task_percent = 100
        except (KeyError):
            if(task.get_status()!= "queued" ):
                status = "Next in Line"
            else:
                status = "Queued"
        try:
            if task.meta['progress'] == 0:
                status = "Next in Line"
            elif 0<task.meta['progress'] <= 1:
                status = "On Conveyor"
            elif 1<task.meta['progress'] <= 3:
                status = "Filling Bottle"
            elif 3<task.meta['progress'] <= 6:
                status = "On Conveyor"
            elif 6<task.meta['progress'] <= 8 :
                status = "Waiting for Kuka Arm"
                if task.meta['lid'] == "true":
                    status = "Lid Station"

            elif 8<task.meta['progress'] <= 10:
                status = "Kuka arm to table"
            else:
                status = "def"
        except (TypeError):
            if task.meta['progress'] == "Success":
                status = "Success"
        except KeyError:
            print("")

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
        #print(data)
        #print(data['runmode'])  # Print selected run options for
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
