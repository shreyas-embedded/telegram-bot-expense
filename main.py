import os
import re
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from google.oauth2.service_account import Credentials

creds_info = json.loads(os.environ['GOOGLE_CREDS_JSON'])
# Set up Google Sheets API
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
gc = gspread.authorize(creds)
# creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
sheet = gspread.authorize(creds).open("Expenses").sheet1

# Telegram bot token from environment or replace below
BOT_TOKEN = os.getenv("BOT_TOKEN") or "7872237058:AAF6ekSXjMPebnUe5h8wZRG_0ECo8uFFD20"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    match = re.search(r'₹\s?(\d+(?:\.\d{1,2})?)', text)
    amount = match.group(1) if match else "0"
    store_match = re.search(r'at\s+(\w+)', text, re.IGNORECASE)
    store = store_match.group(1) if store_match else "Unknown"
    category = "General"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = update.message.from_user.first_name

    sheet.append_row([now, store, amount, category, text, user])
    await update.message.reply_text(f"✅ Saved ₹{amount} at {store} for {user}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
