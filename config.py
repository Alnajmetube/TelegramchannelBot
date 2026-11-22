"""Environment configuration. Importing this module does not require credentials."""

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID", "").strip()
CF_API_TOKEN = os.getenv("CF_API_TOKEN", "").strip()


def validate_config() -> None:
    required = {
        "BOT_TOKEN": BOT_TOKEN,
        "CHANNEL_ID": CHANNEL_ID,
        "CF_ACCOUNT_ID": CF_ACCOUNT_ID,
        "CF_API_TOKEN": CF_API_TOKEN,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError("Missing required environment variables: " + ", ".join(missing))
