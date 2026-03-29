import os
from fastapi import FastAPI, Request
from aiogram import Bot
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = Bot(token=BOT_TOKEN)
app = FastAPI()

async def send_signal(text):
    await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="HTML")

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    symbol = data.get("symbol")
    side = data.get("side")
    entry = data.get("entry")
    sl = data.get("sl")
    tp1 = data.get("tp1")
    tp2 = data.get("tp2")
    tp3 = data.get("tp3")

    message = f"""
🔥 <b>{symbol} {side}</b>

Entry: {entry}
Stop Loss: {sl}

TP1: {tp1}
TP2: {tp2}
TP3: {tp3}

#TradingSignal
"""

    asyncio.create_task(send_signal(message))

    return {"status": "sent"}
