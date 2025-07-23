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

# ✅ Funktion um Token-Daten + Marketcap zu holen
def get_token_info():
    url = f'https://api.dexscreener.io/latest/dex/tokens/{TOKEN_ADDRESS}'
    response = requests.get(url)
    data = response.json()

    pair = data['pairs'][0]
    price = pair.get('priceUsd', 'N/A')
    liquidity = pair['liquidity'].get('usd', 'N/A')
    volume = pair['volume'].get('h24', 'N/A')

    # Marketcap Berechnung (mit Error-Handling)
    circulating_supply = 1000000  # 📝 Setze hier echten Supply ein
    try:
        price_float = float(price)
        marketcap = price_float * circulating_supply
        marketcap_str = f"${marketcap:,.2f}"
    except (ValueError, TypeError):
        marketcap_str = "N/A"

    return (
        f"💰 *Price:* ${price}\n"
        f"📊 *Liquidity:* ${liquidity}\n"
        f"📈 *24h Volume:* ${volume}\n"
        f"🏦 *Marketcap:* {marketcap_str}\n"
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

# ✅ Flask Server
app_server = Flask(__name__)

@app_server.route('/')
def home():
    return "✅ COAI Telegram Bot is alive and listening for Telegram Webhooks!"

@app_server.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot_app.process_update(update))
    loop.close()
    return "OK", 200

# 🚀 Bot starten
async def main():
    global bot_app
    bot_app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

    bot_app.add_handler(CommandHandler('start', start))
    bot_app.add_handler(CommandHandler('ca', ca))

    port = int(os.environ.get('PORT', 8443))
    external_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'coai-bot-3.onrender.com')
    webhook_url = f"https://{external_hostname}/webhook"

    print(f"🤖 Setting webhook to: {webhook_url}")

    await bot_app.initialize()
    await bot_app.bot.set_webhook(webhook_url)

    threading.Thread(target=lambda: app_server.run(host='0.0.0.0', port=port)).start()

    await bot_app.start()
    print("🤖 Telegram Bot is running and ready for Webhooks.")

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
