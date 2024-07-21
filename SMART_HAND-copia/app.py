from flask import Flask, request, jsonify
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('interfaz.html')

@app.route('/api/python_script', methods=['POST'])
def run_python_script():
    data = request.get_json()
    if data.get('command') == 'start_script':
        try:
            subprocess.Popen(['python', 'puntero.py'])
            return jsonify({'status': 'success', 'message': 'Script started'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'status': 'error', 'message': 'Invalid command'}), 400

if __name__ == '__main__':
    app.run(debug=True)




