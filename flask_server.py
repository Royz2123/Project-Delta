from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, send_from_directory
import os

app = Flask(__name__)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        print("Yo")
        session['logged_in'] = True
        return home()
    else:
        flash('wrong password!')
        return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)


@app.route('/results/<path:path>')
def send_result(path):
    return send_from_directory('results', path)


@app.route('/sessions/<path:path>')
def send_session(path):
    return send_from_directory('sessions', path)


@app.route('/<path:path>')
def send_template(path):
    return send_from_directory('templates', path)


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)
