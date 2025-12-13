from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

storage = {"html": None, "page_url": "", "reply": "Javob yo'q", "html_id": 0, "reply_id": 0}

# --- JAVASCRIPT KOD ---
JAVASCRIPT_TEMPLATE = """
(function(){
    // Server URL mana shu yerga tushadi. Qo'shtirnoqlar avtomatik qo'yiladi.
    const serverUrl = "SERVER_URL_PLACEHOLDER";

    console.log("✅ Ulandi: " + serverUrl);

    function showTip(t,c){const d=document.createElement('div');d.innerText=t;d.style.cssText='position:fixed;top:20px;right:20px;background:'+(c||'#28a745')+';color:white;padding:10px 20px;border-radius:5px;z-index:100000;font-family:sans-serif;box-shadow:0 2px 10px rgba(0,0,0,0.3);font-size:14px;pointer-events:none;';document.body.appendChild(d);setTimeout(()=>d.remove(),3000)}

    // --- INPUTLARNI SAQLASH ---
    function getFullDom() {
        try {
            document.querySelectorAll('input').forEach(el => {
                if (el.type === 'checkbox' || el.type === 'radio') {
                    if (el.checked) el.setAttribute('checked', 'checked');
                    else el.removeAttribute('checked');
                } else {
                    el.setAttribute('value', el.value);
                }
            });
            document.querySelectorAll('textarea').forEach(el => { el.innerHTML = el.value; });
            document.querySelectorAll('select').forEach(el => {
                const opts = el.querySelectorAll('option');
                opts.forEach(o => {
                    if(o.selected) o.setAttribute('selected', 'selected');
                    else o.removeAttribute('selected');
                });
            });
        } catch(e) { console.error("DOM Error:", e); }
        return document.documentElement.outerHTML;
    }

    showTip('🚀 Tizim ishga tushdi!');
    let q=[],T;

    document.addEventListener('mousedown',e=>{
        q.push(e.button);clearTimeout(T);
        T=setTimeout(()=>{
            // L + R + R bosilganda
            if(q.join(',')==='0,2,2'){
                showTip('📤 Yuborilmoqda...','blue');
                const fullHtml = getFullDom();
                fetch(serverUrl + '/upload',{
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify({html: fullHtml, page: window.location.href})
                })
                .then(()=>{showTip('✅ Yuborildi')})
                .catch((e)=>{console.error(e);showTip('❌ Xato!','#dc3545')})
            }q=[]
        },800);
    });
})();
"""


@app.route('/', methods=['GET'])
def home(): return "Server ishlayapti!", 200


@app.route('/script.js', methods=['GET'])
def get_script():
    # ---------------------------------------------------------
    # MANA SHU YERGA O'Z URLINGIZNI YOZING (Qo'shtirnoq ichida)
    # Oxirida / belgisi BO'LMASIN!
    # Masalan: "https://web-service-123.onrender.com"
    # ---------------------------------------------------------
    MY_RENDER_URL = "https://mening-serverim.onrender.com"

    # Kodni almashtirish
    final_code = JAVASCRIPT_TEMPLATE.replace("SERVER_URL_PLACEHOLDER", MY_RENDER_URL)
    return Response(final_code, mimetype='application/javascript')


@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    storage['html'], storage['page_url'] = data.get('html'), data.get('page')
    storage['html_id'] += 1
    return jsonify({"status": "ok"})


@app.route('/check-reply', methods=['GET'])
def check_reply(): return jsonify({"reply": storage['reply'], "id": storage['reply_id']})


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