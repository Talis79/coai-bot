import os
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 Token aus .env laden
load_dotenv()
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# 📌 Contract-Adresse & API-Link
TOKEN_ADDRESS = "0x22491EdfafDC9A635085a364ea336ed79df54da3"
DEXSCREENER_API = f"https://api.dexscreener.io/latest/dex/tokens/{TOKEN_ADDRESS}"
DEX_LINK = f"https://dexscreener.com/base/{TOKEN_ADDRESS}"

# 📊 Daten abrufen
def get_token_info():
    try:
        res = requests.get(DEXSCREENER_API)
        data = res.json()["pairs"][0]
        price = float(data["priceUsd"])
        marketcap = float(data["fdv"])
        liquidity = float(data["liquidity"]["usd"])
        volume = float(data["volume"]["h24"])

        return (
            f"📊 *Token Info*\n\n"
            f"💰 *Preis:* ${price:,.8f}\n"
            f"📈 *Market Cap:* ${marketcap:,.0f}\n"
            f"💧 *Liquidität:* ${liquidity:,.0f}\n"
            f"🔄 *24h Volumen:* ${volume:,.0f}\n\n"
            f"🔗 *Contract:* `{TOKEN_ADDRESS}`"
        )
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Daten: {e}")
        return "⚠️ Fehler beim Abrufen der Token-Daten."

# 📥 /ca Command
async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = get_token_info()
    button = InlineKeyboardButton("📊 View on DexScreener", url=DEX_LINK)
    markup = InlineKeyboardMarkup([[button]])
    await update.message.reply_text(info, parse_mode="Markdown", reply_markup=markup)

# 👋 /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome Agent! Type /ca to get current COAI token info.")

# 🚀 Bot starten
async def main():
    app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ca", ca))
    print("🤖 Bot läuft...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
