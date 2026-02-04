# main.py
# Minimal Microdot server: API routes first, static fallback last.

from microdot import Microdot, send_file
from microdot.websocket import with_websocket
import os

STATUS = False

app = Microdot()

# ------------------------------------------------------------------
# 1. API endpoints (MUST be registered before the catch-all)
# ------------------------------------------------------------------
@app.route('/ws/tags')
@with_websocket
async def tags_ws(request, ws):
    """
    Клиент сам выбирает теги:
    +tag_name  - подписаться
    -tag_name  - отписаться
    """
    global broker
    my_topics = set()  # теги, на которые подписан этот сокет

    try:
        while True:
            raw = await ws.receive()  # '+TagName' / '-TagName'
            if not raw or len(raw) < 2:
                continue
            op, topic = raw[0], raw[1:]
            if op == '+':  # подписаться
                if topic not in my_topics:
                    print(f'WS subscribing to topic: {topic}')
                    # broker.subscribe(topic, sender_callback, ws)
                    my_topics.add(topic)
            elif op == '-':  # отписаться
                if topic in my_topics:
                    # broker.unsubscribe(topic, sender_callback, ws)
                    my_topics.discard(topic)
            # g.trigger_all_tags()  # сразу шлём актуальные значения
    except Exception as e:
        print('WS client gone:', e)
    finally:
        # отписываемся от всего при отключении клиента
        for t in my_topics:
            pass
            # broker.unsubscribe(t, sender_callback, ws)


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
