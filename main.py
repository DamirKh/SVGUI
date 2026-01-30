# main.py
# Minimal Microdot server: API routes first, static fallback last.

import os
import time
import asyncio
import json

from microdot import Microdot, send_file
from microdot.websocket import with_websocket

STATUS = False

app = Microdot()

# ------------------------------------------------------------------
# 0. WebSocket
# ------------------------------------------------------------------

@app.route('/ws/tags')
@with_websocket
async def tags_ws(request, ws):
    """
    Send current server tags every second:
    {
      "gauge": <0-59>,        # current second
      "date_str": "YYYY-MM-DD HH:MM:SS"
    }
    """
    try:
        while True:
            t = time.localtime()
            payload = {
                "gauge": 90-t[5],                                     # second
                "date_str": f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d} "
                            f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"
            }
            await ws.send(json.dumps(payload))
            await asyncio.sleep(1)
    except Exception:
        # client disconnected
        pass

# ------------------------------------------------------------------
# 1. API endpoints (MUST be registered before the catch-all)
# ------------------------------------------------------------------
@app.get('/api/status')
async def api_status(request):
    return f'System {STATUS}', 200, {'Content-Type': 'text/plain'}

@app.post('/api/toggle')
async def api_toggle(request):
    global STATUS
    STATUS = not STATUS
    return f'System {STATUS}', 200, {'Content-Type': 'text/plain'}

# ------------------------------------------------------------------
# 2. API: receive set-point from browser
# ------------------------------------------------------------------
SETPOINT = 22.0          # default

@app.post('/api/setpoint')
async def api_setpoint(request):
    """
    Expect JSON: {"setpoint": <float>}
    Return JSON: {"status": "ok", "setpoint": <float>}
    """
    global SETPOINT
    try:
        data = request.json
        if not isinstance(data, dict) or 'setpoint' not in data:
            raise ValueError('missing field')
        sp = float(data['setpoint'])
        if not (5.0 <= sp <= 40.0):          # simple sanity
            raise ValueError('out of range 5-40 °C')
        SETPOINT = round(sp, 1)
        return {'status': 'ok', 'setpoint': SETPOINT}, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        print(e)
        return {'status': 'error', 'msg': str(e)}, 400, {'Content-Type': 'application/json'}

# ------------------------------------------------------------------
# 3. Static file serving (catch-all – keep last)
# ------------------------------------------------------------------
@app.route('/')
async def index(request):
    index_path = os.path.join('www', 'index.html')
    if os.path.isfile(index_path):
        return send_file(index_path)
    return 'index.html not found', 404

@app.route('/<path:path>')
async def static(request, path):
    file_path = os.path.join('www', path)
    if os.path.isfile(file_path):
        return send_file(file_path)
    return 'File not found', 404

# ------------------------------------------------------------------
if __name__ == '__main__':
    app.run(port=8000, debug=True)
