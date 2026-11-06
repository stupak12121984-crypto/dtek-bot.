import os
import re
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = "https://www.dtek-oem.com.ua/ua/shu"

def get_schedule_status():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        if response.status_code != 200:
            return "⚠️ Ошибка загрузки сайта ДТЭК."
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        
        alert_text = ""
        if "відсутня електроенергія" in page_text:
            match_reason = re.search(r'Причина:[^\n]+', page_text)
            match_time = re.search(r'орієнтовний час відновлення[^\n\d]+([\d\.\s:]+)', page_text, re.I)
            reason = match_reason.group(0) if match_reason else "Аварійні роботи"
            time_rest = match_time.group(1) if match_time else ""
            alert_text = f"🔴 <b>Увага! Повідомлення ДТЭК:</b>\n{reason}\n🕒 Відновлення: {time_rest}\n"
        
        now_kyiv = datetime.utcnow() + timedelta(hours=2)
        time_str = now_kyiv.strftime('%H:%M')
        
        msg = f"⚡ <b>Статус ДТЭК (Одесса)</b>\n🕒 Время проверки: {time_str}\n\n"
        if alert_text:
            msg += alert_text + "\n"
        else:
            msg += "🟢 Экстренных аварийных сообщений на сайте не обнаружено.\nГрафик работает в штатном режиме.\n"
            
        return msg
    except Exception as e:
        return f"⚠️ Ошибка обработки: {e}"

def get_keyboard():
    keyboard = [[InlineKeyboardButton("⚡ Проверить свет", callback_data="check_status")]]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Нажмите кнопку ниже, чтобы проверить текущий статус света от ДТЭК:",
        reply_markup=get_keyboard()
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_status":
        text = get_schedule_status()
        await query.message.reply_text(text, parse_mode="HTML", reply_markup=get_keyboard())

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    print("Бот запущен...")
    app.run_polling()
    
