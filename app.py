from collections import deque
from time import sleep

from flask import Flask, request, render_template
from flask_rq2 import RQ

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
        result1 = request.form
        data = request.form.to_dict()
        print(data)
        from jobs import orderProcess
        job = orderProcess.queue(data, queue='orders')
        print(job.result)
        return render_template("result.html", result=result1)


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
