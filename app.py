import socket
import threading
import time
from queue import Queue
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Настройки подключения к ESP8266
ESP_IP = "192.168.100.58"  # ЗАМЕНИТЕ НА ВАШ IP
ESP_PORT = 8888

# Переменные состояния
gcode_queue = Queue()
is_streaming = False

status_data = {
    "status": "Idle",
    "total_lines": 0,
    "sent_lines": 0,
    "current_command": "",
    "buffer_slots": 0,
    "logs": []  # Список для хранения последних ответов
}

def grbl_stream_worker(ip, port, queue):
    global is_streaming, status_data
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect((ip, port))
        
        # Разблокировка GRBL
        s.sendall(b"$X\n")
        time.sleep(0.2)
        
        status_data["status"] = "Streaming"
        status_data["logs"] = ["Connected to ESP8266"]
        
        MAX_BUFFER_COMMANDS = 3
        active_commands = 0
        recv_accumulator = ""
        
        while is_streaming or not queue.empty() or active_commands > 0:
            # 1. Читаем ответы от GRBL
            s.setblocking(False)
            try:
                data = s.recv(1024).decode('utf-8', errors='ignore')
                if data:
                    print(data)
                    recv_accumulator += data
                    while "\n" in recv_accumulator:
                        line, recv_accumulator = recv_accumulator.split("\n", 1)
                        line = line.strip()
                        
                        if line:
                            # Добавляем строку в лог (храним последние 30 строк)
                            status_data["logs"].append(line)
                            if len(status_data["logs"]) > 30:
                                status_data["logs"].pop(0)

                            if "ok" in line or "error" in line:
                                if active_commands > 0:
                                    active_commands -= 1
                                status_data["buffer_slots"] = active_commands
            except BlockingIOError:
                pass
            
            # 2. Отправляем команды, если есть место в буфере
            if is_streaming and active_commands < MAX_BUFFER_COMMANDS and not queue.empty():
                gcode_line = queue.get()
                clean_line = gcode_line.strip()
                
                if clean_line and not clean_line.startswith(";"):
                    s.sendall((clean_line + "\n").encode('utf-8'))
                    active_commands += 1
                    status_data["sent_lines"] += 1
                    status_data["current_command"] = clean_line
                    status_data["buffer_slots"] = active_commands
                
                queue.task_done()
                
            time.sleep(0.001)
            
        status_data["status"] = "Finished"
        s.close()
        
    except Exception as e:
        status_data["status"] = f"Error: {str(e)}"
        status_data["logs"].append(f"ERROR: {str(e)}")
    finally:
        is_streaming = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_gcode():
    global is_streaming, status_data
    if is_streaming:
        return jsonify({"error": "Печать уже запущена"}), 400
        
    gcode_text = request.form.get('gcode', '')
    if not gcode_text:
        return jsonify({"error": "Файл пуст"}), 400
        
    with gcode_queue.mutex:
        gcode_queue.queue.clear()
        
    lines = gcode_text.splitlines()
    for line in lines:
        if line.strip():
            gcode_queue.put(line)
            
    status_data.update({
        "total_lines": gcode_queue.qsize(),
        "sent_lines": 0,
        "status": "Starting...",
        "logs": ["G-Code loaded. Starting stream..."]
    })
    
    is_streaming = True
    thread = threading.Thread(target=grbl_stream_worker, args=(ESP_IP, ESP_PORT, gcode_queue))
    thread.daemon = True
    thread.start()
    
    return jsonify({"success": True, "lines": len(lines)})

@app.route('/status')
def get_status():
    return jsonify(status_data)

@app.route('/stop', methods=['POST'])
def stop_stream():
    global is_streaming
    is_streaming = False
    with gcode_queue.mutex:
        gcode_queue.queue.clear()
    status_data["status"] = "Stopped"
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)