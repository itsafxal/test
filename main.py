import os
from dotenv import load_dotenv
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

load_dotenv()

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# ── Premium emoji ─────────────────────────────────────────────────────────────
PREMIUM_EMOJI = "<emoji id='5796253585100509494'>👋</emoji>"

# ── Raw keyboard builder (supports 'style' field via plain dicts) ─────────────
def build_raw_keyboard(btn_rows):
    """
    Converts a list of button rows into raw Bot API inline_keyboard dicts.
    Each button is either:
      - an InlineKeyboardButton  -> converted to dict
      - already a dict           -> used as-is (supports 'style' field)
    """
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

# ── Keyboards ─────────────────────────────────────────────────────────────────
START_KEYBOARD = InlineKeyboardMarkup(
    build_raw_keyboard([
        [{"text": "🌐 Website", "callback_data": "website", "style": "success"}],
        [{"text": "📞 Support", "callback_data": "support", "style": "primary"}],
        [{"text": "ℹ️  About",  "callback_data": "about",   "style": "danger"}],
    ])
)

BACK_KEYBOARD = InlineKeyboardMarkup(
    build_raw_keyboard([
        [{"text": "🔙 Back", "callback_data": "back"}],
    ])
)

# ── /start handler ────────────────────────────────────────────────────────────
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await message.reply_text(
        f"{PREMIUM_EMOJI} Hello, {message.from_user.mention}!\n\n"
        "Welcome to the bot. Choose an option below:",
        reply_markup=START_KEYBOARD,
        parse_mode=enums.ParseMode.HTML,
    )

# ── Callback query handlers ───────────────────────────────────────────────────
@app.on_callback_query(filters.regex("^website$"))
async def website_callback(client, callback_query: CallbackQuery):
    await callback_query.answer("Opening website…", show_alert=False)
    await callback_query.message.edit_text(
        "🌐 <b>Website</b>\n\nVisit us at: https://example.com",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=BACK_KEYBOARD,
    )

@app.on_callback_query(filters.regex("^support$"))
async def support_callback(client, callback_query: CallbackQuery):
    await callback_query.answer("Connecting to support…", show_alert=False)
    await callback_query.message.edit_text(
        "📞 <b>Support</b>\n\nContact us at: @support_username",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=BACK_KEYBOARD,
    )

@app.on_callback_query(filters.regex("^about$"))
async def about_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "ℹ️ <b>About</b>\n\nThis bot is built with Pyrofork.\nVersion: 1.0.0",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=BACK_KEYBOARD,
    )

@app.on_callback_query(filters.regex("^back$"))
async def back_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text(
        f"{PREMIUM_EMOJI} Hello, {callback_query.from_user.mention}!\n\n"
        "Welcome to the bot. Choose an option below:",
        reply_markup=START_KEYBOARD,
        parse_mode=enums.ParseMode.HTML,
    )

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Bot is running…")
    app.run()
