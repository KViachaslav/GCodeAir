from flask import Flask, render_template, request, jsonify
import time
import socket
app = Flask(__name__)
s = None
def get_socket():
    global s
    if s is None:
        # Создаем сокет, если он еще не создан
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Устанавливаем таймаут, чтобы Flask не завис вечно при ожидании ответа
        s.settimeout(2.0)
    return s
@app.get("/")
def index():
    return render_template("index1.html")
@app.route('/send', methods=['POST'])
def process_gcode():
    global s
    if s is None:
        return jsonify({"error": "Socket not initialized"}), 400
    
    try:    
        data = request.get_json().get('gcode', '')
        # data = request.json.get('gcode', '')
        s.sendall((data + '\n').encode('utf-8'))
        
        # Получаем ответ (если станок что-то присылает)
        response = s.recv(1024).decode('utf-8')
        return jsonify({"result": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
   
    
@app.route('/connect', methods=['POST'])
def connectESP():
    global s
    sock = None
    try:
        data = request.get_json()
        ip = data.get('ip', '')
        port = data.get('port', '')

        if not ip or not port:
            return jsonify({"status": "error", "message": "IP or Port missing"}), 400

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0) 
        
        # 2. Пытаемся подключиться
        sock.connect((ip, int(port)))
        if s:
            try: s.close() 
            except: pass
            
        s = sock
        # Убираем таймаут для последующей работы, если нужно
        s.settimeout(None)
        return jsonify({"status": "connect"})

    except socket.timeout:

        return jsonify({"status": "error", "message": "Connection timed out"}), 408
    except socket.error as e:
        
        return jsonify({"status": "error", "message": f"Socket error: {e}"}), 503
    except Exception as e:
        s = None
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        # Проверяем, был ли сокет создан, прежде чем менять его настройки
        if sock is not None:
            sock.settimeout(None)
    


@app.route('/disconnect')
def disconnectESP():
    # global s
    # s.close()
    # return jsonify({"status": "disconnect"})
    global s
    if s:
        s.close()
        s = None
    return jsonify({"status": "disconnect"})

@app.get("/api/drawing")
def api_drawing():
    return jsonify({
        "width": 800,
        "height": 500,
        "items": [
            {"type": "line", "x1": 50, "y1": 450, "x2": 750, "y2": 450, "stroke": "#000", "w": 2},
            {"type": "circle", "cx": 400, "cy": 250, "r": 80, "stroke": "blue", "w": 3},
            {"type": "poly", "points": [[200,300],[400,120],[600,300]], "stroke": "red", "w": 2, "fill": "rgba(255,0,0,0.15)"}
        ]
    })



if __name__ == "__main__":
    app.run(debug=True)