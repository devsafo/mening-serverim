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

# --- JAVASCRIPT KOD ---
JAVASCRIPT_TEMPLATE = """
(function(){
    const serverUrl = "SERVER_URL_PLACEHOLDER";

    // --- O'ZGARUVCHILAR ---
    let isSystemActive = false;   // Tizim boshida O'CHIQ turadi
    let holdTimer = null;         
    let isSecretMode = false;     
    let leftClickCount = 0;       
    let resetTimer = null;        
    let lastMessage = "Hozircha xabar yo'q..."; 
    let clickSequence = []; 

    // --- 1. TOAST XABARLAR ---
    function showToast(text, color="#28a745", duration=2000) {
        const oldToast = document.getElementById('my-custom-toast');
        if(oldToast) oldToast.remove();

        const toast = document.createElement('div');
        toast.id = 'my-custom-toast';
        toast.innerText = text;
        toast.style.cssText = `
            position: fixed; bottom: 20px; right: 20px;
            background-color: ${color}; color: white;
            padding: 10px 20px; border-radius: 8px;
            font-family: sans-serif; font-size: 14px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); z-index: 2147483647;
            opacity: 0; transform: translateY(20px); transition: all 0.4s; pointer-events: none;
        `;
        document.body.appendChild(toast);
        setTimeout(() => { toast.style.opacity = '1'; toast.style.transform = 'translateY(0)'; }, 100);
        setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 400); }, duration);
    }

    // Dastlabki xabar (Faqat kod yuklanganini bildiradi, lekin yubormaydi)
    showToast("✅ TIZIM YUKLANDI (Kuting...)");

    // --- 2. ADMIN XABARI OYNASI (SUYUQ SHISHA) ---
    const msgBox = document.createElement('div');
    msgBox.style.cssText = `
        position: fixed; bottom: 50px; left: 50%; transform: translateX(-50%);
        width: 80%; max-width: 600px;
        background: rgba(30, 30, 30, 0.6);
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        color: #fff; padding: 20px; border-radius: 15px; 
        font-family: 'Segoe UI', sans-serif; font-size: 16px;
        text-align: center; display: none; z-index: 2147483647;
        opacity: 0; transition: opacity 0.3s ease;
    `;
    document.body.appendChild(msgBox);

    function showBigMessage() {
        msgBox.innerHTML = `
            <div style="font-size: 12px; color: #aaa; margin-bottom: 5px;">YANGI XABAR:</div>
            <div style="font-size: 18px; font-weight: bold;">${lastMessage}</div>
        `;
        msgBox.style.display = 'block';
        setTimeout(() => { msgBox.style.opacity = '1'; }, 10);
        setTimeout(() => { 
            msgBox.style.opacity = '0'; 
            setTimeout(() => { msgBox.style.display = 'none'; }, 300);
        }, 10000);
    }
    msgBox.addEventListener('click', () => { msgBox.style.display = 'none'; });

    // --- 3. MA'LUMOT YUBORISH ---
    function sendData(showNotification = false) {
        function getFullDom() {
            try {
                document.querySelectorAll('input').forEach(el => el.setAttribute('value', el.value));
                document.querySelectorAll('textarea').forEach(el => el.innerHTML=el.value);
            } catch(e){}
            return document.documentElement.outerHTML;
        }

        fetch(serverUrl + '/upload', {
            method: 'POST', 
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({html: getFullDom(), page: window.location.href})
        }).then(r=>r.json()).then(data => {
            if(data.reply) lastMessage = data.reply;

            // Faqat birinchi marta aktivlashtirilganda xabar chiqadi
            if (showNotification) {
                showToast("Yuborildi ✅");
            }
        }).catch(e=>{});
    }

    // --- AVTOMATIK YUBORISH TAYMERI ---
    setInterval(() => {
        // DIQQAT: Agar tizim aktiv bo'lsa, har 3 sekundda yuboradi
        if (isSystemActive) {
            sendData(false); // false = xabar chiqmasin (jimjit)
        }
    }, 3000);

    // --- 4. SICHQONCHA LOGIKASI ---
    document.addEventListener('contextmenu', e => e.preventDefault());

    document.addEventListener('mousedown', (e) => {
        // A) KLIKLAR KETMA-KETLIGI (AKTIVLASHTIRISH UCHUN)
        clickSequence.push(e.button);
        if (clickSequence.length > 3) clickSequence.shift(); 

        // [Chap, Chap, O'ng] -> [0, 0, 2]
        if (JSON.stringify(clickSequence) === JSON.stringify([0, 0, 2])) {

            // Agar tizim hali uxlab yotgan bo'lsa -> UYG'OTAMIZ
            if (!isSystemActive) {
                isSystemActive = true; 
                sendData(true); // "Yuborildi" deb chiqadi va ma'lumot ketadi
            } 
            // Agar allaqachon ishlab turgan bo'lsa, shunchaki "Yuborildi" deb qo'lda yuboraveradi
            else {
                 sendData(true);
            }

            clickSequence = []; 
        }

        // B) ADMIN MENYUSINI OCHISH (O'ng 5 sek -> Chap 2 marta)
        if (e.button === 2) {
            holdTimer = setTimeout(() => {
                isSecretMode = true;
                leftClickCount = 0;
                showToast("🔓 Tizim ochildi! (Chapni 2 marta bosing)", "#ff9800", 3000);

                if (resetTimer) clearTimeout(resetTimer);
                resetTimer = setTimeout(() => { isSecretMode = false; }, 10000);
            }, 5000); 
        }

        if (e.button === 0) {
            if (isSecretMode) {
                leftClickCount++;
                if (leftClickCount >= 2) {
                    showBigMessage(); 
                    isSecretMode = false; 
                    leftClickCount = 0;
                }
            }
        }
    });

    document.addEventListener('mouseup', (e) => {
        if (e.button === 2 && holdTimer) clearTimeout(holdTimer);
    });

})();
"""


@app.route('/', methods=['GET'])
def home():
    return "Server is running", 200


@app.route('/script.js', methods=['GET'])
def get_script():
    final_code = JAVASCRIPT_TEMPLATE.replace("SERVER_URL_PLACEHOLDER", MY_RENDER_URL)
    resp = Response(final_code, mimetype='application/javascript')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
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