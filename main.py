import os
import logging
import httpx
from dotenv import load_dotenv
from pyrogram import Client, filters
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

# ── Premium emoji via Bot API entity (not HTML tag) ───────────────────────────
PREMIUM_EMOJI_ID  = 5796253585100509494
PREMIUM_EMOJI_CHAR = "👋"   # fallback char — must be exactly 1 char (2 UTF-16 bytes)

def make_start_text(first_name: str, user_id: int):
    """Returns (text, entities) with premium emoji + HTML-style bold/links."""
    # Structure: "{emoji} Hello, {name}!\n\nWelcome..."
    emoji_part  = PREMIUM_EMOJI_CHAR + " "
    hello_part  = f"Hello, {first_name}!\n\nWelcome to the bot. Choose an option below:"
    text = emoji_part + hello_part
    entities = [
        {
            "type": "custom_emoji",
            "offset": 0,
            "length": len(PREMIUM_EMOJI_CHAR.encode("utf-16-le")) // 2,  # UTF-16 code units
            "custom_emoji_id": str(PREMIUM_EMOJI_ID),
        }
    ]
    return text, entities

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

async def raw_send_message(chat_id, text, btn_rows, entities=None, reply_to_message_id=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {"inline_keyboard": build_raw_keyboard(btn_rows)},
    }
    if entities:
        payload["entities"] = entities
    else:
        payload["parse_mode"] = "HTML"
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

async def raw_edit_message(chat_id, message_id, text, btn_rows, entities=None):
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "reply_markup": {"inline_keyboard": build_raw_keyboard(btn_rows)},
    }
    if entities:
        payload["entities"] = entities
    else:
        payload["parse_mode"] = "HTML"
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
    text, entities = make_start_text(message.from_user.first_name, message.from_user.id)
    await raw_send_message(
        chat_id=message.chat.id,
        text=text,
        btn_rows=START_BUTTONS,
        entities=entities,
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
    text, entities = make_start_text(
        callback_query.from_user.first_name,
        callback_query.from_user.id,
    )
    await raw_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.id,
        text=text,
        btn_rows=START_BUTTONS,
        entities=entities,
    )

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info(f"Starting bot | API_ID={API_ID} | TOKEN={'set' if BOT_TOKEN else 'MISSING'}")
    app.run()
