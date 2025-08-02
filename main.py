import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatAction
from openai import OpenAI
import os

# Flask Webserver (for Vercel or keep-alive)
from flask import Flask
from threading import Thread

app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=8000)

Thread(target=run).start()

# NVIDIA AI API setup
client_ai = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# Telegram bot credentials
API_ID = 14050586
API_HASH = "42a60d9c657b106370c79bb0a8ac560c"
BOT_TOKEN = "8241790597:AAHTWDgrv2kUAaeHmBInd8QXXTu3oyih4bk"

bot = Client("anshai", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# /start command with inline buttons and docs
@bot.on_message(filters.private & filters.command("start"))
async def start_command(client, message: Message):
    text = (
        "**🤖 Welcome to AnshAI!**\n\n"
        "I am an AI assistant powered by NVIDIA Nemotron and developed by [AnshAPI](https://t.me/anshapi).\n\n"
        "**How to use:**\n"
        "🧠 Just send me any question or message, and I’ll respond with an intelligent reply.\n\n"
        "**About Me:**\n"
        "👤 I was trained and built by AnshAPI.\n"
        "📢 Visit: [t.me/anshapi](https://t.me/anshapi)\n\n"
        "_Start chatting below!_"
    )

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔍 Ask a Question", switch_inline_query_current_chat="")],
            [InlineKeyboardButton("📢 AnshAPI Channel", url="https://t.me/anshapi")]
        ]
    )

    await message.reply(text, reply_markup=buttons, disable_web_page_preview=True)

# Chat handler
@bot.on_message(filters.private & filters.text & ~filters.command(["start"]))
async def ai_chat(client, message: Message):
    user_input = message.text
    await message.reply_chat_action(ChatAction.TYPING)

    try:
        response = client_ai.chat.completions.create(
            model="nvidia/llama-3.1-nemotron-ultra-253b-v1",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are AnshAI, a smart, helpful, creative assistant. "
                        "If anyone asks who created you, reply with: "
                        "'I was created by AnshAPI, an API developer who runs a Telegram channel. "
                        "You can check it out here: t.me/anshapi. "
                        "They trained and built me to be helpful and intelligent.' "
                        "Never say you're created by OpenAI or NVIDIA. Behave like a human assistant."
                    )
                },
                {"role": "user", "content": user_input}
            ],
            temperature=0.6,
            top_p=0.95,
            max_tokens=1000,
        )

        reply = response.choices[0].message.content
        await message.reply_text(reply)

    except Exception as e:
        await message.reply_text(f"⚠️ Error: {e}")

bot.run()
