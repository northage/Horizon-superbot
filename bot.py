import os
import asyncio
from fastapi import FastAPI, Request
from aiogram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

WEBHOOK_SECRET = "horizon123"

bot = Bot(token=BOT_TOKEN)
app = FastAPI()


async def send_signal(text: str):
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        parse_mode="HTML"
    )


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    if data.get("secret") != WEBHOOK_SECRET:
        return {"status": "unauthorized"}

    symbol = data.get("symbol", "N/A")
    side = data.get("side", "N/A")
    signal_price = data.get("signal_price", "N/A")
    entry = data.get("entry", "N/A")
    sl = data.get("sl", "N/A")

    # Take Profits
    tp1 = data.get("tp1", "N/A")
    tp2 = data.get("tp2", "N/A")
    tp3 = data.get("tp3", "N/A")

    message = f"""
🔥 <b>{symbol} {side}</b>

<b>Signal Price:</b> {signal_price}
<b>Entry Range:</b> {entry}
<b>Stop Loss:</b> {sl}

🎯 <b>TP1:</b> {tp1}
🎯 <b>TP2:</b> {tp2}
🎯 <b>TP3:</b> {tp3}
🚀 <b>TP4:</b> Let it run 🚀

⚠️ <i>Manage trade once in profit make safe and trail stop loss up</i> ⚠️
"""

    asyncio.create_task(send_signal(message))

    return {"status": "sent"}
