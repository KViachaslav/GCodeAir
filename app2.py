from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index2.html')

# Пример функции Python, вызываемой из JS
@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    action = data.get('action')
    
    print(f"Выполняю команду из Python: {action}")
    
    # Здесь может быть логика управления станком через последовательный порт
    if action == 'home':
        return jsonify({"status": "success", "message": "Станок отправлен в HOME"})
    
    return jsonify({"status": "error", "message": "Неизвестная команда"})

if __name__ == '__main__':
    app.run(debug=True)