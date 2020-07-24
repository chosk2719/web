from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    menu = {'home':True, 'rgrs':False, 'stmt':False, 'clsf':False, 'clst':False, 'user':False}
    return render_template('home.html', menu=menu)

@app.route('/regression', methods=['GET', 'POST'])
def regression():
    menu = {'home':False, 'rgrs':True, 'stmt':False, 'clsf':False, 'clst':False, 'user':False}
    if request.method == 'GET':
        return render_template('regression.html', menu=menu)
    else:
        iris = {'slen': float(request.form['slen']), 'plen': float(request.form['plen']),
            'pwid': float(request.form['pwid']), 'species': int(request.form['species'])}
        return render_template('reg_result.html', menu=menu, iris=iris)

@app.route('/sentiment')
def sentiment():
    pass

@app.route('/classification')
def classification():
    pass

@app.route('/clustering')
def clustering():
    pass

if __name__ == '__main__':
    app.run(debug=True)