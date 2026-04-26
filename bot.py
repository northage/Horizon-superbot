import os
import logging
from typing import Optional

from fastapi import FastAPI, Request
from aiogram import Bot

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("webhook")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
WEBHOOK_SECRET = "horizon123"

bot = Bot(token=BOT_TOKEN)
app = FastAPI()

# Track the Telegram message_id of the entry signal for each active trade,
# so TP/SL updates can be sent as replies that thread under the entry.
# Keyed by (symbol, side). Cleared when the trade closes (TP5 or SL).
active_trades: dict = {}


async def send_message(text: str, reply_to: Optional[int] = None) -> Optional[int]:
    try:
        msg = await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode="HTML",
            reply_to_message_id=reply_to,
        )
        return msg.message_id
    except Exception as e:
        log.error("Telegram send failed: %s", e)
        return None


def format_entry(data: dict) -> str:
    symbol = data.get("symbol", "N/A")
    side = data.get("side", "N/A")
    signal_price = data.get("signal_price", "N/A")
    entry = data.get("entry", "N/A")
    sl = data.get("sl", "N/A")
    tp1 = data.get("tp1", "N/A")
    tp2 = data.get("tp2", "N/A")
    tp3 = data.get("tp3", "N/A")

    return (
        f"🔥 <b>{symbol} {side}</b>\n"
        f"<b>Signal Price:</b> {signal_price}\n"
        f"<b>Entry Range:</b> {entry}\n"
        f"<b>Stop Loss:</b> {sl}\n"
        f"🎯 <b>TP1:</b> {tp1}\n"
        f"🎯 <b>TP2:</b> {tp2}\n"
        f"🎯 <b>TP3:</b> {tp3}\n"
        f"🚀 <b>TP4:</b> Let it run 🚀\n"
        f"⚠️ <i>Make risk free once in profit and trail stop loss up</i> ⚠️"
    )


def format_update(data: dict) -> Optional[str]:
    """Build a short follow-up message for TP/SL events. Returns None if unrecognized."""
    status = (data.get("status") or "").upper()
    price = data.get("price", "N/A")
    pips_made = data.get("pips_made")

    if "TP1 HIT" in status:
        return (
            f"🎯 <b>TP1 Hit @ {price}</b>\n"
            f"Move stop loss to entry — make the trade risk free."
        )
    if "TP2 HIT" in status:
        return (
            f"🎯 <b>TP2 Hit @ {price}</b> 🔥\n"
            f"Trail stop loss up."
        )
    if "TP3 HIT" in status:
        return (
            f"🎯 <b>TP3 Hit @ {price}</b> 🔥\n"
            f"🚀 <b>Let it run 🚀</b>"
        )
    if "TP4 HIT" in status:
        return (
            f"🎯 <b>TP4 Hit @ {price}</b> 🔥\n"
            f"🚀 <b>To The MOON!! 🚀</b>"
        )
    if "TP5 HIT" in status:
        return f"🎯 <b>TP5 Hit @ {price}</b> 💎 DIAMOND HANDS."
    if "STOP LOSS HIT" in status:
        if pips_made:
            return (
                f"⚠️ <b>Stop Loss Hit @ {price}</b>\n"
                f"Made <b>{pips_made} pips</b> before SL — should have moved trade to break-even."
            )
        return f"🛑 <b>Stop Loss Hit @ {price}</b>"
    return None


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    if data.get("secret") != WEBHOOK_SECRET:
        return {"status": "unauthorized"}

    key = (data.get("symbol", ""), data.get("side", ""))

    # TP/SL update message
    if "status" in data:
        text = format_update(data)
        if text is None:
            log.warning("Unrecognized status: %s", data.get("status"))
            return {"status": "ignored"}

        reply_to = active_trades.get(key)
        await send_message(text, reply_to=reply_to)

        status = (data.get("status") or "").upper()
        if "TP5 HIT" in status or "STOP LOSS HIT" in status:
            active_trades.pop(key, None)

        return {"status": "sent"}

    # Entry signal
    text = format_entry(data)
    msg_id = await send_message(text)
    if msg_id is not None:
        active_trades[key] = msg_id

    return {"status": "sent"}
