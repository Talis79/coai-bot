from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from web3 import Web3
import requests
import os
from dotenv import load_dotenv


# 🔑 Dein BotFather API Token
TELEGRAM_API_TOKEN = '7729276817:AAGi1fDFOy_ntNFhDmmtyOxVA9ZX5yWsMU0'

# 📌 Token-Contract-Adresse (COAI)
TOKEN_ADDRESS = '0x22491EdfafDC9A635085a364ea336ed79df54da3'

# 📡 Base RPC URL (Public Endpoint)
BASE_RPC_URL = 'https://mainnet.base.org'



# 🔗 Web3 Initialisierung
web3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))

# ✅ Funktion um Token-Daten zu holen (on-chain + API)
def get_token_info():
    # DexScreener API
    url = f'https://api.dexscreener.io/latest/dex/tokens/{TOKEN_ADDRESS}'
    response = requests.get(url)
    data = response.json()

    pair = data['pairs'][0]
    price = pair['priceUsd']
    liquidity = pair['liquidity']['usd']
    volume = pair['volume']['h24']
    marketcap = pair['fdv']

    # Total Supply und Decimals on-chain abfragen
    try:
        contract = web3.eth.contract(address=Web3.to_checksum_address(TOKEN_ADDRESS), abi=ERC20_ABI)
        total_supply_raw = contract.functions.totalSupply().call()
        decimals = contract.functions.decimals().call()
        total_supply = total_supply_raw / (10 ** decimals)
        total_supply_formatted = f"{total_supply:,.0f}"  # Kommaformatierung
    except Exception as e:
        print(f"❌ Error fetching on-chain data: {e}")
        total_supply_formatted = "Unknown"

    return (
        f"💰 *Price:* ${price}\n"
        f"📊 *Liquidity:* ${liquidity}\n"
        f"📈 *24h Volume:* ${volume}\n"
        f"🏦 *MarketCap:* ${marketcap}\n"
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

# 🚀 Bot starten
async def main():
    app = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ca', ca))
    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == '__main__':
    import nest_asyncio
    import asyncio
    nest_asyncio.apply()
    asyncio.run(main())
