import sqlite3
from flask import Flask, render_template_string, request, session, redirect
import threading, time, requests, uuid, os

app = Flask(__name__)
app.secret_key = "HENRY-X-SECRET-KEY"
DB_NAME = "henry_x.db"

# Initialize Database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''CREATE TABLE IF NOT EXISTS threads 
                    (id TEXT PRIMARY KEY, sid TEXT, token TEXT, tid TEXT, prefix TEXT, delay INTEGER, msgs TEXT, running INTEGER, paused INTEGER)''')
    conn.commit()
    conn.close()

init_db()

def worker(tkey, token, tid, prefix, delay, msgs):
    url = f'https://graph.facebook.com/v15.0/t_{tid}/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    while True:
        conn = sqlite3.connect(DB_NAME)
        row = conn.execute("SELECT running, paused FROM threads WHERE id=?", (tkey,)).fetchone()
        if not row or not row[0]: break
        if row[1]: 
            time.sleep(1)
            continue
        
        for msg in msgs:
            requests.post(url, data={'access_token': token, 'message': f"{prefix} {msg}"}, headers=headers)
            time.sleep(int(delay))
        conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'sid' not in session: session['sid'] = str(uuid.uuid4())
    sid = session['sid']
    
    if request.method == 'POST':
        tkey = str(uuid.uuid4())[:8]
        token = request.form['token']
        tid = request.form['tid']
        prefix = request.form['prefix']
        delay = request.form['delay']
        msgs = request.form['msgs'].splitlines()
        
        conn = sqlite3.connect(DB_NAME)
        conn.execute("INSERT INTO threads VALUES (?,?,?,?,?,?,?,?,?)", (tkey, sid, token, tid, prefix, delay, "\n".join(msgs), 1, 0))
        conn.commit()
        threading.Thread(target=worker, args=(tkey, token, tid, prefix, delay, msgs)).start()
        
    conn = sqlite3.connect(DB_NAME)
    threads = conn.execute("SELECT * FROM threads WHERE sid=?", (sid,)).fetchall()
    conn.close()
    return render_template_string(HTML, threads=threads)

HTML = '''
<style>
    body { background: linear-gradient(135deg, #4b0082, #ff0000); color: white; font-family: monospace; }
    .card { background: rgba(0,0,0,0.6); padding: 15px; border-radius: 10px; margin: 10px; border: 1px solid #ff0055; }
</style>
<h1 align="center" style="font-size: 50px;">HENRY-X SERVER</h1>
<form method="POST" class="card" style="max-width: 500px; margin: auto;">
    <input name="token" placeholder="Access Token" class="w-full bg-black p-2 mb-2">
    <input name="tid" placeholder="Thread ID" class="w-full bg-black p-2 mb-2">
    <input name="delay" placeholder="Delay" class="w-full bg-black p-2 mb-2">
    <input name="prefix" placeholder="Prefix" class="w-full bg-black p-2 mb-2">
    <textarea name="msgs" placeholder="Messages" class="w-full bg-black p-2 mb-2"></textarea>
    <button class="w-full bg-red-600 p-2">START HENRY-X</button>
</form>
'''

if __name__ == '__main__':
    app.run(port=5000)
