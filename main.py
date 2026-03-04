from flask import Flask, render_template_string, request, redirect, url_for
import threading, time, requests, uuid

app = Flask(__name__)
# Thread storage
threads = {}

def send_messages(t_id, token, prefix, delay, messages, t_key):
    headers = {'User-Agent': 'Mozilla/5.0'}
    threads[t_key]['logs'] = ["🚀 Bot Initialized..."]
    
    while threads[t_key]['active']:
        if threads[t_key]['paused']:
            time.sleep(1)
            continue
            
        for msg in messages:
            if not threads[t_key]['active']: break
            full_msg = f"{prefix} {msg}"
            try:
                # Yeh code tumhare worker/send_message function ke andar dalo
try:
    res = requests.post(
        f'https://graph.facebook.com/v18.0/{thread_id}/messages', # Endpoint update kiya
        data={'access_token': token, 'message': full_msg}, 
        headers=headers
    )
    # ASLI ERROR DEKHNE KE LIYE:
    if res.status_code == 200:
        log = "✅ SENT"
    else:
        log = f"❌ FAILED - Code: {res.status_code} - Reason: {res.text}" 
    print(log) # Terminal mein dekho
    threads[t_key]['logs'].append(log)
except Exception as e:
    print(f"⚠️ ERROR: {e}")

@app.route('/')
def index():
    return render_template_string(HTML_CODE, threads=threads)

@app.route('/start', methods=['POST'])
def start():
    t_key = str(uuid.uuid4())[:8]
    data = request.form
    messages = data['msgs'].splitlines()
    threads[t_key] = {'tid': data['tid'], 'active': True, 'paused': False, 'logs': []}
    threading.Thread(target=send_messages, args=(data['tid'], data['token'], data['prefix'], data['delay'], messages, t_key)).start()
    return redirect('/')

@app.route('/action/<t_key>/<action>')
def action(t_key, action):
    if t_key in threads:
        if action == 'pause': threads[t_key]['paused'] = True
        elif action == 'resume': threads[t_key]['paused'] = False
        elif action == 'stop': threads[t_key]['active'] = False
        elif action == 'del': del threads[t_key]
    return redirect('/')

HTML_CODE = '''
<!DOCTYPE html>
<html>
<head>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(to bottom, #4b0082, #ff0000); color: white; min-height: 100vh; }
        .glass { background: rgba(0,0,0,0.6); backdrop-filter: blur(10px); }
    </style>
</head>
<body class="p-6">
    <h1 class="text-3xl font-bold text-center mb-8">HENRY-X PRO TERMINAL</h1>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="glass p-6 rounded-xl border border-red-500">
            <form action="/start" method="post">
                <input name="token" required placeholder="Access Token" class="w-full p-2 mb-2 bg-black rounded">
                <input name="tid" required placeholder="Thread ID" class="w-full p-2 mb-2 bg-black rounded">
                <input name="prefix" placeholder="Prefix" class="w-full p-2 mb-2 bg-black rounded">
                <input type="number" name="delay" value="5" placeholder="Delay" class="w-full p-2 mb-2 bg-black rounded">
                <textarea name="msgs" placeholder="Messages (Line by line)" class="w-full p-2 mb-2 bg-black h-32 rounded"></textarea>
                <button class="w-full bg-red-600 hover:bg-purple-700 p-3 rounded font-bold">START HENRY-X</button>
            </form>
        </div>
        <div>
            {% for k, v in threads.items() %}
            <div class="glass p-4 rounded-xl mb-4 border border-purple-500">
                <div class="flex justify-between">
                    <span>Thread: {{v.tid}}</span>
                    <div>
                        <a href="/action/{{k}}/pause" class="text-orange-500 mx-2">Pause</a>
                        <a href="/action/{{k}}/resume" class="text-blue-500 mx-2">Resume</a>
                        <a href="/action/{{k}}/stop" class="text-red-500 mx-2">Stop</a>
                        <a href="/action/{{k}}/del" class="text-gray-500 mx-2">Del</a>
                    </div>
                </div>
                <div class="mt-2 text-xs h-20 overflow-y-scroll bg-black p-2">
                    {% for l in v.logs[-5:] %}<p>{{l}}</p>{% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
