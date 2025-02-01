import csv
from flask import Flask, render_template, jsonify, request
from util import *

app = Flask(__name__)

# temporary sensor data
sensors = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/logs')
def logs():
    with open('log/watering_log.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        logs = list(reader)
    return render_template('logs.html', logs=logs)


@app.route('/api/sensors', methods=['GET', 'POST'])
def api_sensors():
    global sensors
    if request.method == 'POST':
        sensors = request.json  # Daten vom Client
    return jsonify(sensors)


if __name__ == '__main__':
    # configuration
    config = get_configuration()
    IP_ADDRESS = config[3]
    PORT = config[4]

    app.run(host=IP_ADDRESS, port=PORT, debug=True)
