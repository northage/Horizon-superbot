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

    message = f"""
🔥 <b>{symbol} {side}</b>

<b>Signal Price:</b> {signal_price}
<b>Entry Range:</b> {entry}
<b>Stop Loss:</b> {sl}

⚠️ <i>Manage trade once in profit make safe and trial stop loss up</i> ⚠️
"""

    asyncio.create_task(send_signal(message))

    return {"status": "sent"}
