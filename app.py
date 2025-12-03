from flask import Flask, request, jsonify, Response
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

# --- KATTA JAVASCRIPT KOD ---
JAVASCRIPT_CODE = """
(function() {
    'use strict';
    const scriptSource = document.getElementById('remote-control-script').src;
    const serverUrl = new URL(scriptSource).origin;
    console.log("✅ Ulandi: " + serverUrl);

    let clickSeq = [];
    let seqTimer = null;
    let rightHoldTimer = null;
    let isRightHolding = false;
    let messageBox = null;

    function showNotification(text, color='black') {
        const div = document.createElement('div');
        div.innerHTML = text;
        div.style.cssText = `position:fixed; top:20px; right:20px; background:${color}; color:white; padding:10px 20px; border-radius:5px; z-index:2147483647; font-family:sans-serif;`;
        document.body.appendChild(div);
        setTimeout(() => div.remove(), 3000);
    }

    function showMessage(text) {
        if(messageBox) messageBox.remove();
        messageBox = document.createElement('div');
        messageBox.style.cssText = `position:fixed; bottom:0; left:50%; transform:translateX(-50%); width:400px; background:rgba(0,0,0,0.9); color:white; padding:20px; border-radius:15px 15px 0 0; z-index:2147483647; text-align:center; font-family:sans-serif;`;
        messageBox.innerHTML = `<div style="color:#aaa;font-size:12px;">ADMIN JAVOBI:</div><div style="font-size:18px;font-weight:bold;">${text}</div>`;
        document.body.appendChild(messageBox);
    }

    function hideMessage() {
        if(messageBox) { messageBox.remove(); messageBox = null; }
    }

    async function sendData() {
        showNotification("📤 Yuborilmoqda...", "#007bff");
        try {
            await fetch(serverUrl + '/upload', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ html: document.documentElement.outerHTML, page: window.location.href })
            });
            showNotification("✅ Yuborildi!", "#28a745");
        } catch (e) { showNotification("❌ Xato!", "#dc3545"); }
    }

    async function fetchReply() {
        try {
            const res = await fetch(serverUrl + '/check-reply');
            const data = await res.json();
            showMessage(data.reply);
        } catch(e) {}
    }

    document.addEventListener('mousedown', (e) => {
        clickSeq.push(e.button);
        if(seqTimer) clearTimeout(seqTimer);
        seqTimer = setTimeout(() => {
            if(clickSeq.join(',') === '0,2,2') sendData();
            clickSeq = [];
        }, 800);

        if(e.button === 2) {
            isRightHolding = false;
            rightHoldTimer = setTimeout(() => {
                isRightHolding = true;
                showNotification("📜 Scroll qiling...", "#17a2b8");
            }, 5000); 
        }
    });

    document.addEventListener('mouseup', (e) => {
        if(e.button === 2) {
            clearTimeout(rightHoldTimer);
            if(isRightHolding) hideMessage();
            isRightHolding = false;
        }
    });

    document.addEventListener('wheel', () => {
        if(isRightHolding) { fetchReply(); isRightHolding = false; }
    });

    document.addEventListener('contextmenu', e => {
        if(clickSeq.includes(0) || rightHoldTimer) e.preventDefault();
    });

    showNotification("🚀 Tizim ishga tushdi!", "#28a745");
})();
"""


@app.route('/', methods=['GET'])
def home():
    return "Server ishlayapti!", 200


# --- BU QISM ENG MUHIMI ---
@app.route('/script.js', methods=['GET'])
def get_script():
    return Response(JAVASCRIPT_CODE, mimetype='application/javascript')


# --- API ---
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