import asyncio
import aiohttp
import json
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

# ─── Flask Web Server ─────────────────────────────────────────────
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    web_app.run(host='0.0.0.0', port=8080)  # 👈 Custom Port here

def keep_alive():
    thread = Thread(target=run_flask)
    thread.start()

# ─── Bot Config ───────────────────────────────────────────────────
API_ID = 14050586
API_HASH = "42a60d9c657b106370c79bb0a8ac560c"
BOT_TOKEN = "8381216775:AAEyjjTHyvLUm3nBjbYbXrm7K38OPVY0GE4"

app = Client("info_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ─── Start Command ────────────────────────────────────────────────
@app.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Call Tracer Info", callback_data="call_tracer")],
        [InlineKeyboardButton("🚗 Vehicle Info", callback_data="vehicle_info")]
    ])
    await message.reply("Welcome! Choose an option:", reply_markup=keyboard)

# ─── Handle Button Clicks ─────────────────────────────────────────
@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    if data == "call_tracer":
        await callback_query.message.reply("📞 Send the phone number (10 digits):")
        await callback_query.answer()
        app.call_tracer_user[user_id] = True
    elif data == "vehicle_info":
        await callback_query.message.reply("🚗 Send the vehicle number (e.g. UP32AB1234):")
        await callback_query.answer()
        app.vehicle_info_user[user_id] = True

# ─── Handle Text Messages ─────────────────────────────────────────
@app.on_message(filters.text & ~filters.command(["start"]))
async def handle_queries(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    # 📞 Call Tracer Info
    if app.call_tracer_user.get(user_id):
        await message.reply("⏳ Fetching call tracer info...")
        url = f"https://calltracerinfoapi.vercel.app/api?number={text}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    text_data = await resp.text()
                    json_data = json.loads(text_data)
            formatted = "<b>📞 Call Tracer Info:</b>\n"
            for key, value in json_data.items():
                value = "N/A" if value in ["", None] else str(value)
                formatted += f"<b>{key.replace('_', ' ').title()}:</b> {value}\n"
            await message.reply(formatted)
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
        app.call_tracer_user[user_id] = False

    # 🚗 Vehicle Info
    elif app.vehicle_info_user.get(user_id):
        await message.reply("⏳ Fetching vehicle info...")
        url = f"https://vechileinfoapi.anshppt19.workers.dev/api/rc?number={text}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    json_data = await resp.json()
            formatted = "<b>🚗 Vehicle Info:</b>\n"
            for key, value in json_data.items():
                value = "N/A" if value in ["", None] else str(value)
                formatted += f"<b>{key.replace('_', ' ').title()}:</b> {value}\n"
            await message.reply(formatted)
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
        app.vehicle_info_user[user_id] = False

# ─── User State Dicts ─────────────────────────────────────────────
app.call_tracer_user = {}
app.vehicle_info_user = {}

# ─── Start Everything ─────────────────────────────────────────────
keep_alive()  # 🟢 Start Flask on port 8080
app.run()     # ▶️ Start Telegram bot
