import socket

esp_ip = "192.168.1.58" 
port = 8888 

try:
   
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2) 
    
    print(f"Подключение к {esp_ip}...")
    s.connect((esp_ip, port))
    
    print("Соединение установлено!")
    s.sendall(b"G28\n")
    
    data = s.recv(1024)
    print("Ответ от ESP:", data.decode())

except PermissionError:
    print("Ошибка прав! Попробуй запустить VS Code от имени Администратора.")
except Exception as e:
    print(f"Не удалось подключиться: {e}")
finally:
    s.close()