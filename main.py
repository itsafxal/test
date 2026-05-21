import os
from dotenv import load_dotenv
from pyrogram import Client, filters

load_dotenv()  # loads variables from .env into os.environ
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Load credentials from environment variables
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# ── Inline keyboard with 3 buttons ──────────────────────────────────────────
START_KEYBOARD = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🌐 Website",  callback_data="website")],
        [InlineKeyboardButton("📞 Support",  callback_data="support")],
        [InlineKeyboardButton("ℹ️  About",    callback_data="about")],
    ]
)

# ── /start handler ────────────────────────────────────────────────────────────
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await message.reply_text(
        f"👋 Hello, {message.from_user.mention}!\n\n"
        "Welcome to the bot. Choose an option below:",
        reply_markup=START_KEYBOARD,
    )

# ── Callback query handlers ───────────────────────────────────────────────────
@app.on_callback_query(filters.regex("^website$"))
async def website_callback(client, callback_query: CallbackQuery):
    await callback_query.answer("Opening website…", show_alert=False)
    await callback_query.message.edit_text(
        "🌐 **Website**\n\nVisit us at: https://example.com",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
        ),
    )

@app.on_callback_query(filters.regex("^support$"))
async def support_callback(client, callback_query: CallbackQuery):
    await callback_query.answer("Connecting to support…", show_alert=False)
    await callback_query.message.edit_text(
        "📞 **Support**\n\nContact us at: @support_username",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
        ),
    )

@app.on_callback_query(filters.regex("^about$"))
async def about_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "ℹ️ **About**\n\nThis bot is built with Pyrogram v2.\nVersion: 1.0.0",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
        ),
    )

@app.on_callback_query(filters.regex("^back$"))
async def back_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text(
        f"👋 Hello, {callback_query.from_user.mention}!\n\n"
        "Welcome to the bot. Choose an option below:",
        reply_markup=START_KEYBOARD,
    )

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Bot is running…")
    app.run()
