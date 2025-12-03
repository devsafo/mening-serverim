from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Ma'lumotlar ombori
storage = {
    "html": None,
    "page_url": "",
    "reply": "Javob yo'q",
    "html_id": 0,
    "reply_id": 0
}

@app.route('/', methods=['GET'])
def home():
    return "Server ishlayapti!", 200

# --- BRAUZER UCHUN ---
@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    storage['html'] = data.get('html')
    storage['page_url'] = data.get('page')
    storage['html_id'] += 1
    return jsonify({"status": "ok"})

@app.route('/check-reply', methods=['GET'])
def check_reply():
    return jsonify({"reply": storage['reply'], "id": storage['reply_id']})

# --- DESKTOP ILOVA UCHUN ---
@app.route('/admin-check', methods=['GET'])
def admin_check():
    return jsonify({"html_id": storage['html_id'], "url": storage['page_url']})

@app.route('/admin-get-html', methods=['GET'])
def admin_get_html():
    return jsonify({"html": storage['html']})

@app.route('/admin-reply', methods=['POST'])
def admin_reply():
    data = request.json
    storage['reply'] = data.get('message')
    storage['reply_id'] += 1
    return jsonify({"status": "sent"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)