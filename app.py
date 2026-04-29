from flask import Flask, render_template, request, jsonify
import time
app = Flask(__name__)

@app.get("/")
def index():
    return render_template("ind.html")
@app.route('/process', methods=['POST'])
def process_gcode():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'result': 'No data'}), 400
            
        line = data.get('gcode', '')
        
        time.sleep(1)
        transformed = line.upper() + " ; OK" 
        
        return jsonify({'result': transformed})
        
    except Exception as e:
        
        return jsonify({'result': f'Error: {str(e)}'}), 500
    
@app.route('/reset')
def reset():
    # Какая-то логика сброса в Python
    return jsonify({"status": "Система сброшена"})

if __name__ == "__main__":
    app.run(debug=True)