import os
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 Token aus .env laden
load_dotenv()
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# 📌 Token Contract-Adresse (COAI)
TOKEN_ADDRESS = '0x22491EdfafDC9A635085a364ea336ed79df54da3'
DEXSCREENER_URL = f"https://api.dexscreener.io/latest/dex/tokens/{TOKEN_ADDRESS}"
DEX_LINK = f"https://dexscreener.com/base/{TOKEN_ADDRESS}"

# 📊 Token-Daten abrufen
def get_token_info():
    try:
        response = requests.get(DEXSCREENER_URL)
        data = response.json()
        pair = data['pairs'][0]

        price = pair['priceUsd']
        liquidity = pair['liquidity']['usd']
        volume = pair['volume']['h24']
        marketcap = pair['fdv']

        return (
            f"📊 *Token Info*\n\n"
            f"💰 *Price:* ${float(price):,.8f}\n"
            f"📈 *Market Cap:* ${int(float(marketcap)):,}\n"
            f"💧 *Liquidity:* ${int(float(liquidity)):,}\n"
            f"🔄 *24h Volume:* ${int(float(volume)):,}\n\n"
            f"🔗 *Contract:* `{TOKEN_ADDRESS}`"
        )
    except Exception as e:
        print(f"❌ Fehler beim Abrufen: {e}")
        return "⚠️ Fehler beim Abrufen der Token-Daten."

# 👋 /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome Agent! Type /ca to get current COAI token info.")

# 💵 /ca Command
async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = get_token_info()
    button = InlineKeyboardButton("📊 View on DexScreener", url=DEX_LINK)
    reply_markup = InlineKeyboardMarkup([[button]])
    await update.message.reply_text(info, reply_markup=reply_markup, parse_mode='Markdown')

# 🚀 Hauptfunktion
async def main():
    app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ca", ca))
    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
