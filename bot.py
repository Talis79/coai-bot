from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import os
import threading
import nest_asyncio
import asyncio

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

    return (
        f"💰 *Price:* ${price}\n"
        f"📊 *Liquidity:* ${liquidity}\n"
        f"📈 *24h Volume:* ${volume}\n"
        f"🔗 *Contract:* `{TOKEN_ADDRESS}`"
    )

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

# Flask App für Render Dummy Server und Webhook
app_server = Flask(__name__)

@app_server.route('/')
def home():
    return "✅ COAI Telegram Bot is alive and listening for Telegram Webhooks!"

@app_server.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.run(bot_app.process_update(update))
    return "OK", 200

# 🚀 Bot starten
async def main():
    global bot_app
    bot_app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

    bot_app.add_handler(CommandHandler('start', start))
    bot_app.add_handler(CommandHandler('ca', ca))
    bot_app.add_handler(CommandHandler('marketcap', marketcap))
    bot_app.add_handler(CommandHandler('welcome', welcome))

    # Render-Webservice Settings
    port = int(os.environ.get('PORT', 8443))
    external_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'coai-bot-3.onrender.com')
    webhook_url = f"https://{external_hostname}/webhook"

    print(f"🤖 Setting webhook to: {webhook_url}")

    await bot_app.initialize()
    await bot_app.bot.set_webhook(webhook_url)

    # Start Flask Dummy HTTP Server
    threading.Thread(target=lambda: app_server.run(host='0.0.0.0', port=port)).start()

    await bot_app.start()
    await bot_app.updater.start_polling()
    await bot_app.updater.idle()

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
