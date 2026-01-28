# main.py
# Minimal Microdot server: API routes first, static fallback last.

from microdot import Microdot, send_file
import os

STATUS = False

app = Microdot()

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
# 2. Static file serving (catch-all – keep last)
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
    app.run(host='127.0.0.1', port=8000, debug=True)
