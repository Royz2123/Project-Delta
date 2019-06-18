from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, send_from_directory
import os
import threading
import get_diffs
import time
import logging
import camera_selenium
import sys

logging.basicConfig(level=logging.CRITICAL)
app = Flask(__name__)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')


@app.route('/login', methods=['POST'])
def do_admin_login():
    camera_selenium.username = request.form['username']
    camera_selenium.password = request.form['password']
    session['logged_in'] = True
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


@app.route('/fonts/<path:path>')
def send_font(path):
    return send_from_directory('fonts', path)


@app.route('/sessions/<path:path>')
def send_session(path):
    return send_from_directory('sessions', path)


@app.route('/<path:path>')
def send_template(path):
    if path == "gallery.html":
        try:
            day_index = int(request.args.get('day'))
            hour_index = int(request.args.get('hour'))
            get_diffs.update_gallery(day_index=day_index, hour_index=hour_index)
        except Exception as e:
            print(e)
    return send_from_directory('templates', path)

"""
@app.route('/gallery.html', methods=['GET'])
def gallery():
    print("LOLLLL")
    try:
        index = int(request.form['num'])
        logging.critical(index)
        get_diffs.update_gallery(index=index)
    except Exception as e:
        logging.critical(e.with_traceback())
    finally:
        return send_from_directory('templates', "gallery.html")
"""

if __name__ == "__main__":
    app.secret_key = os.urandom(12)

    threading.Thread(target=app.run, args=('0.0.0.0', 4000, False)).start()
    threading.Thread(target=get_diffs.run_session, args=("z_outdoor4", False)).start()
    # threading.Thread(target=create_session.main).start()

    while True:
        time.sleep(2)

