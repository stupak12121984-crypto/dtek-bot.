import os
import re
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = "https://grad.ua/blackout/105872"

def parse_time_intervals(text):
    intervals = []
    matches = re.findall(r'з\s*(\d{2}:\d{2})\s*до\s*(\d{2}:\d{2})', text)
    for start_str, end_str in matches:
        start_h, start_m = map(int, start_str.split(':'))
        end_h, end_m = map(int, end_str.split(':'))
      
