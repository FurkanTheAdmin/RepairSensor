"""Flask web app showing live occupancy status for 4 repair slots."""

import atexit

from flask import Flask, jsonify, render_template

import config
from sensors import SlotMonitor

app = Flask(__name__)
monitor = SlotMonitor()
monitor.start()
atexit.register(monitor.stop)


@app.route("/")
def index():
    return render_template("index.html", slots=monitor.get_states())


@app.route("/api/status")
def api_status():
    return jsonify(slots=monitor.get_states())


if __name__ == "__main__":
    app.run(host=config.WEB_HOST, port=config.WEB_PORT)
