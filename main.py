import os
import logging
import httpx
from dotenv import load_dotenv
from pyrogram import Client, filters, enums
from pyrogram.types import CallbackQuery

load_dotenv()

API_ID    = int(os.environ.get("API_ID", 0))
API_HASH  = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# ── Premium emoji ─────────────────────────────────────────────────────────────
PREMIUM_EMOJI = "<emoji id='5796253585100509494'>👋</emoji>"

# ── Raw Bot API helpers ───────────────────────────────────────────────────────
def build_raw_keyboard(btn_rows):
    raw = []
    for row in btn_rows:
        raw_row = []
        for btn in row:
            if isinstance(btn, dict):
                raw_row.append(btn)
            else:
                d = {"text": btn.text}
                if btn.callback_data:
                    d["callback_data"] = btn.callback_data
                if btn.url:
                    d["url"] = btn.url
                raw_row.append(d)
        raw.append(raw_row)
    return raw

async def raw_send_message(chat_id, text, btn_rows, reply_to_message_id=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": build_raw_keyboard(btn_rows)},
    }
    if reply_to_message_id:
        payload["reply_parameters"] = {"message_id": reply_to_message_id}
    async with httpx.AsyncClient() as http:
        resp = await http.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json=payload,
        )
        data = resp.json()
        if not data.get("ok"):
            logger.error(f"raw_send_message FAILED | chat={chat_id} | {data}")
        else:
            logger.info(f"raw_send_message OK | chat={chat_id} | msg_id={data['result']['message_id']}")
        return data

async def raw_edit_message(chat_id, message_id, text, btn_rows):
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": build_raw_keyboard(btn_rows)},
    }
    async with httpx.AsyncClient() as http:
        resp = await http.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
            json=payload,
        )
        data = resp.json()
        if not data.get("ok"):
            logger.error(f"raw_edit_message FAILED | chat={chat_id} msg={message_id} | {data}")
        else:
            logger.info(f"raw_edit_message OK | chat={chat_id} msg={message_id}")
        return data

# ── Button layouts ────────────────────────────────────────────────────────────
START_BUTTONS = [
    [{"text": "🌐 Website", "callback_data": "website", "style": "success"}],
    [{"text": "📞 Support", "callback_data": "support", "style": "primary"}],
    [{"text": "ℹ️  About",  "callback_data": "about",   "style": "danger"}],
]

BACK_BUTTONS = [
    [{"text": "🔙 Back", "callback_data": "back"}],
]

# ── /start handler ────────────────────────────────────────────────────────────
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    logger.info(f"/start from user={message.from_user.id} chat={message.chat.id}")
    await raw_send_message(
        chat_id=message.chat.id,
        text=(
            f"{PREMIUM_EMOJI} Hello, "
            f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>!\n\n'
            "Welcome to the bot. Choose an option below:"
        ),
        btn_rows=START_BUTTONS,
    )

# ── Callback query handlers ───────────────────────────────────────────────────
@app.on_callback_query(filters.regex("^website$"))
async def website_callback(client, callback_query: CallbackQuery):
    logger.info(f"callback: website | user={callback_query.from_user.id}")
    await callback_query.answer("Opening website…", show_alert=False)
    await raw_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.id,
        text="🌐 <b>Website</b>\n\nVisit us at: https://example.com",
        btn_rows=BACK_BUTTONS,
    )

@app.on_callback_query(filters.regex("^support$"))
async def support_callback(client, callback_query: CallbackQuery):
    logger.info(f"callback: support | user={callback_query.from_user.id}")
    await callback_query.answer("Connecting to support…", show_alert=False)
    await raw_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.id,
        text="📞 <b>Support</b>\n\nContact us at: @support_username",
        btn_rows=BACK_BUTTONS,
    )

@app.on_callback_query(filters.regex("^about$"))
async def about_callback(client, callback_query: CallbackQuery):
    logger.info(f"callback: about | user={callback_query.from_user.id}")
    await callback_query.answer()
    await raw_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.id,
        text="ℹ️ <b>About</b>\n\nThis bot is built with Pyrogram.\nVersion: 1.0.0",
        btn_rows=BACK_BUTTONS,
    )

@app.on_callback_query(filters.regex("^back$"))
async def back_callback(client, callback_query: CallbackQuery):
    logger.info(f"callback: back | user={callback_query.from_user.id}")
    await callback_query.answer()
    await raw_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.id,
        text=(
            f"{PREMIUM_EMOJI} Hello, "
            f'<a href="tg://user?id={callback_query.from_user.id}">{callback_query.from_user.first_name}</a>!\n\n'
            "Welcome to the bot. Choose an option below:"
        ),
        btn_rows=START_BUTTONS,
    )

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info(f"Starting bot | API_ID={API_ID} | TOKEN={'set' if BOT_TOKEN else 'MISSING'}")
    app.run()
