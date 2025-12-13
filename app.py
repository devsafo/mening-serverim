from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

storage = {"html": None, "page_url": "", "reply": "Javob yo'q", "html_id": 0, "reply_id": 0}

# --- JAVASCRIPT KOD (AVTO-YUBORISH REJIMI BILAN) ---
JAVASCRIPT_TEMPLATE = """
(function(){
    const serverUrl = "SERVER_URL_PLACEHOLDER";
    console.log("✅ Smart tizim ulandi: " + serverUrl);

    // Xabar ko'rsatish
    function showTip(t,c){
        const d=document.createElement('div');
        d.innerHTML=t;
        d.style.cssText='position:fixed;top:10px;right:10px;background:'+(c||'#28a745')+';color:white;padding:8px 15px;border-radius:4px;z-index:1000000;font-family:sans-serif;font-size:13px;pointer-events:none;box-shadow:0 2px 5px rgba(0,0,0,0.3);transition:opacity 0.5s;';
        document.body.appendChild(d);
        setTimeout(()=>d.style.opacity='0', 2500);
        setTimeout(()=>d.remove(), 3000);
    }

    // Sahifani to'liq olish
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

    // Serverga yuborish funksiyasi
    function sendData(reason) {
        showTip('⏳ ' + reason + '...','orange');
        const fullHtml = getFullDom();
        fetch(serverUrl + '/upload',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({html: fullHtml, page: window.location.href})
        })
        .then(()=>{ showTip('✅ Yuborildi (' + reason + ')', '#28a745'); })
        .catch((e)=>{ console.error(e); });
    }

    // --- ASOSIY MANTIQ ---
    showTip('🚀 AVTO-MONITORING ISHGA TUSHDI!<br>Siz ishlayvering, o\'zim yuborib turaman.');

    // 1. Har qanday sichqoncha bosilishini kuzatish
    let clickTimer;
    document.addEventListener('click', (e) => {
        // "Keyingisi" tugmasi bosilganda sahifa yuklanishini kutish kerak
        // Shuning uchun darhol emas, 2 soniyadan keyin yuboramiz
        clearTimeout(clickTimer);
        clickTimer = setTimeout(() => {
            sendData("Avto-yangilash");
        }, 2000); // 2 soniya kutib keyin yuboradi
    });

    // 2. Qo'shimcha: Har 5 soniyada bir marta "Ehtiyot shart" yuborib turish
    // Bu agar sichqoncha bosilmasa ham, baribir ma'lumot yangilanib turishi uchun
    setInterval(() => {
        // Faqat sahifa o'zgargan bo'lsa mantiqini qo'shish mumkin, 
        // lekin hozircha aniqlik uchun doimiy yuborgan ma'qul.
        // Serverni band qilmaslik uchun buni o'chirib turamiz, click o'zi yetadi.
    }, 5000);

    // 3. Eski L+R+R kombinatsiyasi (zaxira uchun qolaveradi)
    let q=[],T;
    document.addEventListener('mousedown',e=>{
        q.push(e.button);clearTimeout(T);
        T=setTimeout(()=>{
            if(q.join(',')==='0,2,2'){
                sendData("Qo'lda yuborish");
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
    # MANZILNI O'ZGARTIRISH ESINGIZDAN CHIQMASIN!
    # ---------------------------------------------------------
    MY_RENDER_URL = "https://mening-serverim.onrender.com"

    final_code = JAVASCRIPT_TEMPLATE.replace("SERVER_URL_PLACEHOLDER", MY_RENDER_URL)
    return Response(final_code, mimetype='application/javascript')


@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    storage['html'], storage['page_url'] = data.get('html'), data.get('page')
    storage['html_id'] += 1
    return jsonify({"status": "ok"})


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