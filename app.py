import modules.yandexmusic as yandex
from modules.functions import CustomFormatter
import logging


# create logger with 'spam_application'
logger = logging.getLogger('application')
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

from flask import Flask, redirect, send_file, request
from flask_executor import Executor
app = Flask(__name__, static_url_path='')
executor = Executor(app)

@app.route("/")
def root():
    return "Wah UwU OwO >w< ^w^ ;3 Yiff"

@app.route("/yandex-music/new-releases")
def yandexmusic_new_releases_rss():
    username = request.args.get('username', default = None)
    return send_file(f'rss/yandexmusic-{username}.xml')

@app.route("/api/yandex-music/new-releases/feed-update")
def feed_update():
    username = request.args.get('username', default = None)
    fetch = request.args.get('fetch', default = 50)
    if username is None:
        cookie_file = None
    else:
        cookie_file = f'uploads/cookies-yandexmusic-{username}.txt'
    executor.submit(yandex.fetch_new_releases, cookie_file, username, fetch)
    return redirect("/", 302)

if __name__ == "__main__":
    app.run(debug=True)