# flask_example.py
# Flask应用示例

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return {"message": "Hello, Flask with Gunicorn!"}

@app.route('/api/data')
def get_data():
    """返回JSON数据的API端点"""
    data = {
        "name": "Flask Application",
        "version": "1.0.0",
        "server": "Gunicorn"
    }
    return jsonify(data)

@app.route('/api/echo', methods=['POST'])
def echo():
    """回显请求数据的API端点"""
    if request.is_json:
        data = request.get_json()
        return jsonify({"received": data})
    else:
        return jsonify({"error": "Request must be JSON"}), 400

if __name__ == '__main__':
    # 用于本地开发的运行方式
    app.run(debug=True, host='0.0.0.0', port=5000)