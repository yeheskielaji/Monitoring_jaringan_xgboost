from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from app.predict import get_prediction, X
import threading
import time
import os

# Inisialisasi aplikasi Flask dan Flask-SocketIO
app = Flask(__name__, static_folder="../frontend", static_url_path="")
socketio = SocketIO(app, cors_allowed_origins="*")

# Variabel global untuk kontrol simulasi
simulation_running = False


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_data = request.get_json(force=True)
        row_index = input_data.get('row_index', 0)
        response = get_prediction(row_index)

        # Kirim data prediksi via WebSocket
        socketio.emit('prediction', response)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def simulate_real_time():
    global simulation_running
    try:
        for i in range(len(X)):
            if not simulation_running:
                break
            response = get_prediction(i)
            socketio.emit('prediction', response)
            time.sleep(1)
    except Exception as e:
        print(f"Error during simulation: {str(e)}")


@socketio.on('start_simulation')
def start_simulation():
    global simulation_running
    simulation_running = True
    print("Simulation started!")
    emit('simulation_started', {'message': 'Simulation Started!'})
    thread = threading.Thread(target=simulate_real_time)
    thread.start()


@socketio.on('stop_simulation')
def stop_simulation():
    global simulation_running
    simulation_running = False
    print("Simulation stopped!")
    emit('simulation_stopped', {'message': 'Simulation Stopped!'})


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'data': 'Connected to Flask-SocketIO'})


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
