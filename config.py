import os
from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_ID = os.getenv("CHANNEL_ID")

AI_API_KEY = os.getenv("AI_API_KEY")

CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing")

if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID is missing")

if not AI_API_KEY:
    raise ValueError("AI_API_KEY is missing")