import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Хранилище загруженного G-кода (в реальном проекте лучше использовать сессии или БД)
gcode_storage = {'content': '''G90 ; абсолютные
G0 X0 Y0 Z0
G1 X20 Y0 Z0 F500
G1 X20 Y20 Z0
G1 X0 Y20 Z0
G1 X0 Y0 Z0
G0 Z5
G1 X20 Y0 Z5
G1 X20 Y20 Z5
G1 X0 Y20 Z5
G1 X0 Y0 Z5
G0 Z0
G1 X0 Y0 Z20
G1 X20 Y0 Z20
G1 X20 Y20 Z20
G1 X0 Y20 Z20
G1 X0 Y0 Z20
G0 X0 Y0 Z0
; диагональ для красоты
G1 X20 Y20 Z20
G1 X0 Y0 Z0
G1 X20 Y0 Z20
G1 X0 Y20 Z0;'''}

@app.route('/')
def index():
    return render_template('index3.html')

@app.route('/upload_gcode', methods=['POST'])
def upload_gcode():
    data = request.get_json()
    gcode_content = data.get('gcode', '')
    gcode_storage['content'] = gcode_content
    return jsonify({'status': 'ok', 'message': 'G-code получен'})

@app.route('/get_gcode')
def get_gcode():
    return jsonify({'gcode': gcode_storage['content']})

if __name__ == '__main__':
    app.run(debug=True)