from pathlib import Path
from dotenv import load_dotenv
import telebot
import os


load_dotenv()
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
bot_token = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telebot.TeleBot(bot_token)

