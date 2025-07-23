from flask import Flask

# Dummy HTTP server for Render
app_server = Flask(__name__)

@app_server.route('/')
def home():
    return "🤖 COAI Telegram Bot is running!"

def run_http_server():
    port = int(os.environ.get('PORT', 5000))
    app_server.run(host='0.0.0.0', port=port)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import os

# 🔑 Dein BotFather API Token
TELEGRAM_API_TOKEN = '7729276817:AAGi1fDFOy_ntNFhDmmtyOxVA9ZX5yWsMU0'

# 📌 Token-Contract-Adresse (COAI)
TOKEN_ADDRESS = '0x22491EdfafDC9A635085a364ea336ed79df54da3'

# ✅ Funktion um Token-Daten zu holen
def get_token_info():
    url = f'https://api.dexscreener.io/latest/dex/tokens/{TOKEN_ADDRESS}'
    response = requests.get(url)
    data = response.json()

    pair = data['pairs'][0]
    price = pair['priceUsd']
    liquidity = pair['liquidity']['usd']
    volume = pair['volume']['h24']

    return f"💰 *Price:* ${price}\n📊 *Liquidity:* ${liquidity}\n📈 *24h Volume:* ${volume}\n🔗 *Contract:* `{TOKEN_ADDRESS}`"

# 👋 /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('👋 Welcome Agent! Type /ca to get current COAI token info.')

# 💵 /ca Command
async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = get_token_info()
    keyboard = [
        [InlineKeyboardButton("View on DexScreener", url=f"https://dexscreener.io/base/{TOKEN_ADDRESS}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(info, reply_markup=reply_markup, parse_mode='Markdown')

# 🆕 /marketcap Command (Platzhalter)
async def marketcap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 Coming soon: Marketcap command.")

# 🆕 /welcome Command
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔒 Access granted. Welcome Agent.")

# 🚀 Bot starten
async def main():
    app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ca', ca))
    app.add_handler(CommandHandler('marketcap', marketcap))
    app.add_handler(CommandHandler('welcome', welcome))

    # Render-Webservice Settings
    port = int(os.environ.get('PORT', 8443))
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"

    print(f"🤖 Setting webhook to: {webhook_url}")

    await app.bot.set_webhook(webhook_url)
    await app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook"
    )

import threading

if __name__ == '__main__':
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()

    # Start dummy HTTP server in a separate thread
    threading.Thread(target=run_http_server).start()

    # Start Telegram Bot (Webhook)
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
