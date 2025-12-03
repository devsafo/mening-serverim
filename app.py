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

# --- KATTA JAVASCRIPT KOD (Server ichida turadi) ---
# Bu kod sizning talablaringizga moslab yozildi:
# 1. L+R+R = Yuborish
# 2. O'ng 5 sekund + Scroll = Javobni ko'rish
JAVASCRIPT_CODE = """
(function() {
    'use strict';
    // Server manzilini avtomatik aniqlash (script qayerdan yuklangan bo'lsa)
    const scriptSource = document.getElementById('remote-control-script').src;
    const serverUrl = new URL(scriptSource).origin;

    console.log("✅ Remote Control Ulandi! Server: " + serverUrl);

    let clickSeq = [];
    let seqTimer = null;
    let rightHoldTimer = null;
    let isRightHolding = false;
    let messageBox = null;

    // --- VIZUAL XABARLAR ---
    function showNotification(text, color='black') {
        const div = document.createElement('div');
        div.innerHTML = text;
        div.style.cssText = `position:fixed; top:20px; right:20px; background:${color}; color:white; padding:10px 20px; border-radius:5px; z-index:2147483647; font-family:sans-serif; box-shadow:0 2px 10px rgba(0,0,0,0.3);`;
        document.body.appendChild(div);
        setTimeout(() => div.remove(), 3000);
    }

    function showMessage(text) {
        if(messageBox) messageBox.remove();
        messageBox = document.createElement('div');
        messageBox.style.cssText = `
            position: fixed; bottom: -300px; left: 50%; transform: translateX(-50%);
            width: 400px; background: rgba(0,0,0,0.9); color: white;
            padding: 20px; border-radius: 15px 15px 0 0; 
            font-family: sans-serif; font-size: 16px; transition: bottom 0.4s;
            z-index: 2147483647; box-shadow: 0 -5px 25px rgba(0,0,0,0.5);
            backdrop-filter: blur(5px); text-align: center; border: 1px solid #444;
        `;
        messageBox.innerHTML = `<div style="color:#aaa;font-size:12px;">ADMIN JAVOBI:</div><div style="font-size:18px;font-weight:bold;">${text}</div>`;
        document.body.appendChild(messageBox);
        requestAnimationFrame(() => messageBox.style.bottom = "0");
    }

    function hideMessage() {
        if(messageBox) {
            messageBox.style.bottom = "-300px";
            setTimeout(() => { if(messageBox) messageBox.remove(); messageBox = null; }, 400);
        }
    }

    // --- SERVER BILAN ALOQA ---
    async function sendData() {
        showNotification("📤 Ma'lumot yuborilmoqda...", "#007bff");
        try {
            await fetch(serverUrl + '/upload', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ html: document.documentElement.outerHTML, page: window.location.href })
            });
            showNotification("✅ Yuborildi!", "#28a745");
        } catch (e) { showNotification("❌ Xatolik!", "#dc3545"); }
    }

    async function fetchReply() {
        try {
            const res = await fetch(serverUrl + '/check-reply');
            const data = await res.json();
            showMessage(data.reply);
        } catch(e) { console.log(e); }
    }

    // --- TUGMALAR ---
    document.addEventListener('mousedown', (e) => {
        // L+R+R
        clickSeq.push(e.button);
        if(seqTimer) clearTimeout(seqTimer);
        seqTimer = setTimeout(() => {
            if(clickSeq.join(',') === '0,2,2') sendData();
            clickSeq = [];
        }, 800);

        // O'ng tugma 5 soniya
        if(e.button === 2) {
            isRightHolding = false;
            rightHoldTimer = setTimeout(() => {
                isRightHolding = true;
                console.log("Scrollga tayyor");
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

    showNotification("🚀 Tizim ishga tushdi!");
})();
"""


@app.route('/', methods=['GET'])
def home():
    return "Server ishlayapti!", 200


# --- YANGI: JAVASCRIPTNI TARQATISH YO'LI ---
@app.route('/script.js', methods=['GET'])
def get_script():
    return Response(JAVASCRIPT_CODE, mimetype='application/javascript')


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