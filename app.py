from flask import Flask, render_template, request

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
        result = request.form
        data = request.form.to_dict()
        print(data)
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
