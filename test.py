import socket
import time

def send_gcode(ip, port, filename):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Подключение к {ip}:{port}...")
            s.connect((ip, port))
            print("Соединение установлено.")

            with open(filename, 'r') as f:
                for line in f:
                    command = line.strip()
                    if not command or command.startswith(';'):
                        continue
                    
                    print(f"Отправка: {command}")
                    s.sendall((command + '\n').encode())

                    # Ждем подтверждения от станка (GRBL обычно присылает 'ok')
                    response = s.recv(1024).decode()
                    print(f"Ответ: {response.strip()}")

    except Exception as e:
        print(f"Ошибка: {e}")

# Использование
ESP_IP = "192.168.100.58" # Впишите IP, который появится на экране Arduino
PORT = 8888
FILE = "project.gcode"

# Раскомментируйте для запуска:
send_gcode(ESP_IP, PORT, FILE)