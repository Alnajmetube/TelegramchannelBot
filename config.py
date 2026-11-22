import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHAT_ID = os.getenv("CHAT_ID")
AI_API_KEY = os.getenv("AI_API_KEY")

CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID")
CF_API_TOKEN = os.getenv("CF_API_TOKEN")

# التحقق من المتغيرات الأساسية عند التشغيل
required_vars = {
    "BOT_TOKEN": BOT_TOKEN,
    "CHANNEL_ID": CHANNEL_ID,
    "AI_API_KEY": AI_API_KEY,
    "CF_ACCOUNT_ID": CF_ACCOUNT_ID,
    "CF_API_TOKEN": CF_API_TOKEN,
}

for name, value in required_vars.items():
    if not value:
        raise ValueError(f"{name} is missing")
        
