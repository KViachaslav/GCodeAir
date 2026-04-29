from flask import Flask, render_template, request, jsonify
import time
import socket
app = Flask(__name__)
s = 0
@app.get("/")
def index():
    return render_template("index.html")
@app.route('/send', methods=['POST'])
def process_gcode():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'result': 'No data'}), 400
            
        line = data.get('gcode', '')
        s.sendall((line + '\n').encode())
        response = s.recv(1024).decode()
        
        return jsonify({'result': response.strip()})
        
    except Exception as e:
        
        return jsonify({'result': f'Error: {str(e)}'}), 500
    
@app.route('/connect', methods=['POST'])
def connectESP():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'result': 'No data'}), 400
        


        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       
        s.connect((data.get('ip', ''), data.get('port', ''))) 



        print(data.get('ip', ''),data.get('port', ''))
        return jsonify({"status": "connect"})
        
    except Exception as e:
        
        return jsonify({'result': f'Error: {str(e)}'}), 500
    # return jsonify({"status": "connect"})



@app.route('/disconnect')
def disconnectESP():
    s.close()
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