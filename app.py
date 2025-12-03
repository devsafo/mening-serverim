from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

storage = {"html": None, "page_url": "", "reply": "Javob yo'q", "html_id": 0, "reply_id": 0}

# --- SIZNING CHIROYLI DIZAYNLI KODINGIZ ---
JAVASCRIPT_CODE = """
(function(){
    const serverUrl = window.location.origin.includes('onrender') ? window.location.origin : 'https://mening-serverim.onrender.com';

    function showTip(t,c){const d=document.createElement('div');d.innerText=t;d.style.cssText='position:fixed;top:20px;right:20px;background:'+(c||'#28a745')+';color:white;padding:10px 20px;border-radius:5px;z-index:100000;font-family:sans-serif;box-shadow:0 2px 10px rgba(0,0,0,0.3);font-size:14px;';document.body.appendChild(d);setTimeout(()=>d.remove(),3000)}
    function showBox(txt){const b=document.createElement('div');b.id='adm-msg-box';b.style.cssText='position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:400px;background:rgba(0,0,0,0.9);color:white;padding:20px;border-radius:15px 15px 0 0;z-index:2147483647;text-align:center;font-family:sans-serif;box-shadow:0 -5px 25px rgba(0,0,0,0.5);border:1px solid #444;';b.innerHTML='<div style="color:#aaa;font-size:12px;margin-bottom:8px;">ADMIN JAVOBI:</div><div style="font-size:18px;font-weight:bold;">'+txt+'</div>';document.body.appendChild(b)}
    function hideBox(){const b=document.getElementById('adm-msg-box');if(b)b.remove()}

    showTip('🚀 Tizim ishga tushdi!');
    let q=[],T,H,ih=false;

    document.addEventListener('mousedown',e=>{
        q.push(e.button);clearTimeout(T);
        T=setTimeout(()=>{
            if(q.join(',')==='0,2,2'){
                showTip('📤 Yuborilmoqda...','blue');
                fetch('https://mening-serverim.onrender.com/upload',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({html:document.documentElement.outerHTML,page:window.location.href})})
                .then(()=>{showTip('✅ Yuborildi')}).catch(()=>{showTip('❌ Xato!','#dc3545')})
            }q=[]
        },800);
        if(e.button===2){ih=false;H=setTimeout(()=>{ih=true;showTip('📜 Scroll qiling...','orange')},5000)}
    });

    document.addEventListener('mouseup',e=>{if(e.button===2){clearTimeout(H);if(ih)hideBox();ih=false}});
    document.addEventListener('wheel',()=>{if(ih){fetch('https://mening-serverim.onrender.com/check-reply').then(r=>r.json()).then(d=>{showBox(d.reply)});ih=false}});
})();
"""


@app.route('/', methods=['GET'])
def home(): return "Server ishlayapti!", 200


# Kodni tarqatuvchi manzil
@app.route('/script.js', methods=['GET'])
def get_script():
    # Koddagi server manzilini to'g'rilash (o'zingiznikiga moslash)
    # Muhim: Quyidagi URLni o'zingizning RENDER manzilingizga o'zgartiring!
    MY_URL = "https://mening-serverim.onrender.com"
    final_code = JAVASCRIPT_CODE.replace("https://mening-serverim.onrender.com", MY_URL)
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