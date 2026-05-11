import os
import asyncio
import aiohttp
from flask import Flask, request, jsonify
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
TIMEZONE = pytz.timezone('Asia/Dushanbe')

events_store = []

async def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'}
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=payload)

def check_and_send_reminders():
    today = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
    today_events = [e for e in events_store if e.get('date') == today and not e.get('sent', False)]
    if today_events:
        message = "🐂🐑 НАПОМИНАНИЕ НА СЕГОДНЯ\n\n"
        for event in today_events:
            message += f"🔔 {event['type']} — {event.get('animal_name', 'животное')}\n"
        asyncio.run(send_telegram_message(message))

@app.route('/api/add_event', methods=['POST'])
def add_event():
    data = request.json
    events_store.append({'id': len(events_store)+1, **data, 'sent': False})
    return jsonify({'status': 'ok'})

@app.route('/')
def index():
    return f'Бот работает! Время: {datetime.now(TIMEZONE).strftime("%H:%M:%S")}'

scheduler = BackgroundScheduler(timezone=TIMEZONE)
scheduler.add_job(check_and_send_reminders, 'cron', hour=8, minute=0)
scheduler.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
