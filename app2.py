import socket
import threading
import time
from queue import Queue
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

ESP_IP = "192.168.100.58"
ESP_PORT = 8888

gcode_queue = Queue()
stream_thread = None
is_streaming = False

# Добавили поле console_log
status_data = {
    "status": "Idle",
    "total_lines": 0,
    "sent_lines": 0,
    "current_command": "",
    "buffer_slots": 0,
    "console_log": [] 
}

def add_to_log(message):
    """Добавляет сообщение в лог и держит последние 20 записей"""
    status_data["console_log"].append(message)
    if len(status_data["console_log"]) > 20:
        status_data["console_log"].pop(0)

def grbl_stream_worker(ip, port, queue):
    global is_streaming, status_data
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect((ip, port))
        
        s.sendall(b"$X\n")
        add_to_log(">>> $X (Unlock)")
        time.sleep(0.2)
        
        status_data["status"] = "Streaming"
        MAX_BUFFER_COMMANDS = 3
        active_commands = 0
        recv_accumulator = ""
        
        while is_streaming or not queue.empty() or active_commands > 0:
            # Чтение ответов
            s.setblocking(False)
            try:
                data = s.recv(1024).decode('utf-8', errors='ignore')
                if data:
                    recv_accumulator += data
                    while "\n" in recv_accumulator:
                        line, recv_accumulator = recv_accumulator.split("\n", 1)
                        line = line.strip()
                        if line:
                            add_to_log(f"<<< {line}") # Записываем ответ в лог
                        
                        if "ok" in line or "error" in line:
                            if active_commands > 0:
                                active_commands -= 1
                            status_data["buffer_slots"] = active_commands
            except BlockingIOError:
                pass
            
            # Отправка команд
            if active_commands < MAX_BUFFER_COMMANDS and not queue.empty():
                gcode_line = queue.get().strip()
                if gcode_line and not gcode_line.startswith(";"):
                    s.sendall((gcode_line + "\n").encode('utf-8'))
                    # add_to_log(f">>> {gcode_line}") # Опционально: писать отправку в лог
                    active_commands += 1
                    status_data["sent_lines"] += 1
                    status_data["current_command"] = gcode_line
                    status_data["buffer_slots"] = active_commands
                queue.task_done()
                
            time.sleep(0.001)
            
        status_data["status"] = "Finished"
        s.close()
        
    except Exception as e:
        status_data["status"] = f"Error: {str(e)}"
        add_to_log(f"SYSTEM ERROR: {e}")
    finally:
        is_streaming = False

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/upload', methods=['POST'])
def upload_gcode():
    global is_streaming, status_data
    if is_streaming: return jsonify({"error": "Занято"}), 400
    gcode_text = request.form.get('gcode', '')
    
    with gcode_queue.mutex: gcode_queue.queue.clear()
    status_data["console_log"] = [] # Очистка лога перед стартом
    
    lines = [line for line in gcode_text.splitlines() if line.strip()]
    for line in lines: gcode_queue.put(line)
            
    status_data.update({"total_lines": len(lines), "sent_lines": 0, "status": "Starting..."})
    is_streaming = True
    threading.Thread(target=grbl_stream_worker, args=(ESP_IP, ESP_PORT, gcode_queue), daemon=True).start()
    return jsonify({"success": True})

@app.route('/status')
def get_status():
    return jsonify(status_data)

@app.route('/stop', methods=['POST'])
def stop_stream():
    global is_streaming
    is_streaming = False
    status_data["status"] = "Stopped"
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)