import contextlib
import modules.yandexmusic as yandex
from modules.functions import CustomFormatter
import logging
import secrets
import os
import pathlib
import json

# create logger with 'spam_application'
logger = logging.getLogger('application')
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

from flask import Flask, redirect, send_file, request, url_for, flash, send_from_directory, render_template, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest, BadRequestKeyError
from flask_executor import Executor
UPLOAD_FOLDER = 'uploads'
RSS_FOLDER = 'rss'
ALLOWED_EXTENSIONS = {'txt'}
app = Flask(__name__, static_url_path='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RSS_FOLDER'] = RSS_FOLDER
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
executor = Executor(app)

@app.route("/")
def root():
    
    os.makedirs(RSS_FOLDER, exist_ok=True)
    feeds = []

    root = pathlib.Path(RSS_FOLDER)
    for path, subdirs, files in os.walk(root):
        for name in files:
            file = pathlib.PurePath(path, name)
            file = os.path.split(file)
            path = file[0]
            username = file[1].split('.xml')[0]
            feeds.append([path, username])
    with contextlib.suppress(KeyError):
        upload_response = json.loads(session['upload_response'])
        session['upload_response'] = json.dumps({})
        return render_template('index.html', feeds=feeds, feed_uri=upload_response.get('feed_uri'), update_uri=upload_response.get('update_uri'))
    return render_template('index.html', feeds=feeds)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('upload.html')
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    try:
        service = request.form['service']
    except BadRequestKeyError:
        flash('Service isn\'t selected')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], service), exist_ok=True)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], service, filename))
        if service == 'yandex-music':
            session['upload_response'] = json.dumps({"feed_uri": f'{request.host_url}{RSS_FOLDER}/yandex-music/new-releases?username={file.filename.split(".")[0]}', "update_uri": f'{request.host_url}api/yandex-music/new-releases/feed-update?username={file.filename.split(".")[0]}'})
            executor.submit(yandex.fetch_new_releases, f"{app.config['UPLOAD_FOLDER']}/yandex-music/{file.filename}", file.filename.split(".")[0], 25)
            return redirect("/", 302)
    else: 
        flash('invalid extension or filename, only ".txt" is allowed')
    return redirect(request.url)

@app.route(f"/{RSS_FOLDER}/yandex-music/new-releases")
def yandexmusic_new_releases_rss():
    username = request.args.get('username', default = None)
    #return send_file(f'rss/{username}.xml')
    return send_from_directory(RSS_FOLDER, f'yandex-music/new-releases/{username}.xml')
    
@app.route("/api/yandex-music/new-releases/feed-update")
def feed_update():
    username = request.args.get('username', default = None)
    fetch = request.args.get('fetch', default = 25)
    if username is None:
        cookie_file = None
    else:
        cookie_file = f"{UPLOAD_FOLDER}/yandex-music/{username}.txt"
    executor.submit(yandex.fetch_new_releases, cookie_file, username, fetch)
    return redirect("/", 302)

if __name__ == "__main__":
    app.run(debug=True)